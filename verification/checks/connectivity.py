"""
Connectivity verification checks.

Tests cross-cluster connectivity by deploying test pods and verifying
network reachability to ILB endpoints.
"""

import time
import subprocess
from typing import Optional
from kubernetes import client, config


class ConnectivityChecker:
    """Checks cross-cluster connectivity using test pods."""

    TEST_POD_NAME = "connectivity-test"
    TEST_POD_IMAGE = "nicolaka/netshoot:latest"

    def __init__(self, cfg: dict, project_id: Optional[str], verbose: bool = False):
        self.cfg = cfg
        self.project_id = project_id
        self.verbose = verbose
        self.results = []

    def _log(self, message: str):
        """Log verbose messages."""
        if self.verbose:
            print(f"  [DEBUG] {message}")

    def _get_k8s_client(self, context: str):
        """Get Kubernetes client for a specific context."""
        try:
            config.load_kube_config(context=context)
            return client.CoreV1Api()
        except Exception as e:
            self._log(f"Failed to load kubeconfig for context {context}: {e}")
            raise

    def _create_test_pod(self, api: client.CoreV1Api, namespace: str) -> bool:
        """Create a test pod for connectivity testing."""
        pod_manifest = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=self.TEST_POD_NAME,
                namespace=namespace,
                labels={"app": "connectivity-test"}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="test",
                        image=self.TEST_POD_IMAGE,
                        command=["sleep", "3600"],
                    )
                ],
                restart_policy="Never"
            )
        )

        try:
            api.create_namespaced_pod(namespace=namespace, body=pod_manifest)
            self._log(f"Created test pod in namespace {namespace}")

            # Wait for pod to be ready
            for _ in range(30):
                pod = api.read_namespaced_pod(name=self.TEST_POD_NAME, namespace=namespace)
                if pod.status.phase == "Running":
                    self._log("Test pod is running")
                    return True
                time.sleep(2)

            self._log("Test pod did not become ready in time")
            return False
        except client.exceptions.ApiException as e:
            if e.status == 409:  # Already exists
                self._log("Test pod already exists")
                return True
            raise

    def _delete_test_pod(self, api: client.CoreV1Api, namespace: str):
        """Delete the test pod."""
        try:
            api.delete_namespaced_pod(
                name=self.TEST_POD_NAME,
                namespace=namespace,
                body=client.V1DeleteOptions(grace_period_seconds=0)
            )
            self._log(f"Deleted test pod from namespace {namespace}")
        except client.exceptions.ApiException as e:
            if e.status != 404:
                self._log(f"Failed to delete test pod: {e}")

    def _test_connectivity(self, context: str, namespace: str,
                          target_ip: str, target_port: int,
                          timeout: int = 5) -> tuple[bool, str]:
        """Test connectivity from a cluster to a target IP:port."""
        try:
            # Use kubectl exec to test connectivity
            cmd = [
                "kubectl", "--context", context,
                "-n", namespace,
                "exec", self.TEST_POD_NAME, "--",
                "nc", "-zv", "-w", str(timeout), target_ip, str(target_port)
            ]

            self._log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)

            if result.returncode == 0:
                return True, f"Connected in {timeout}s"
            else:
                return False, f"Connection failed: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _test_http_connectivity(self, context: str, namespace: str,
                                target_ip: str, target_port: int,
                                path: str = "/ready",
                                timeout: int = 5) -> tuple[bool, str]:
        """Test HTTP connectivity from a cluster to a target."""
        try:
            cmd = [
                "kubectl", "--context", context,
                "-n", namespace,
                "exec", self.TEST_POD_NAME, "--",
                "curl", "-sf", "-m", str(timeout),
                f"http://{target_ip}:{target_port}{path}"
            ]

            self._log(f"Running: {' '.join(cmd)}")
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
            elapsed = int((time.time() - start) * 1000)

            if result.returncode == 0:
                return True, f"HTTP 200 in {elapsed}ms"
            else:
                return False, f"HTTP request failed: {result.returncode}"

        except subprocess.TimeoutExpired:
            return False, "HTTP timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def run_checks(self) -> list:
        """Run all connectivity checks."""
        self.results = []

        # Get cluster configurations
        clusters = self.cfg.get('clusters', {})
        connectivity_tests = self.cfg.get('connectivity_tests', [])

        # Process each cluster that needs a test pod
        test_clusters = set(t['source_cluster'] for t in connectivity_tests)

        for cluster_name in test_clusters:
            cluster_cfg = clusters.get(cluster_name, {})
            context = cluster_cfg.get('context', f"gke-{cluster_name}")
            namespace = cluster_cfg.get('namespace', 'bank-of-anthos')

            self._log(f"Setting up test pod in cluster {cluster_name}")

            try:
                api = self._get_k8s_client(context)

                # Create test pod
                if not self._create_test_pod(api, namespace):
                    self.results.append({
                        'name': f"Test pod setup ({cluster_name})",
                        'passed': False,
                        'details': "Failed to create test pod"
                    })
                    continue

                # Run connectivity tests for this cluster
                for test in connectivity_tests:
                    if test['source_cluster'] != cluster_name:
                        continue

                    target_ip = test['target_ip']
                    target_port = test['target_port']
                    test_name = test['name']

                    self._log(f"Testing: {test_name}")

                    # Determine if this is HTTP or TCP test
                    if target_port == 8085:
                        passed, details = self._test_http_connectivity(
                            context, namespace, target_ip, target_port
                        )
                    else:
                        passed, details = self._test_connectivity(
                            context, namespace, target_ip, target_port
                        )

                    expected_success = test.get('expected', 'success') == 'success'
                    actual_passed = passed == expected_success

                    self.results.append({
                        'name': f"C1→C2: {test_name}" if cluster_name == 'c1' else f"C2→C1: {test_name}",
                        'passed': actual_passed,
                        'details': details
                    })

            except Exception as e:
                self._log(f"Error in cluster {cluster_name}: {e}")
                self.results.append({
                    'name': f"Connectivity tests ({cluster_name})",
                    'passed': False,
                    'details': str(e)
                })

            finally:
                # Cleanup test pod
                try:
                    api = self._get_k8s_client(context)
                    self._delete_test_pod(api, namespace)
                except Exception:
                    pass

        return self.results
