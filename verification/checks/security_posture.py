"""
Security posture verification checks.

Verifies that the infrastructure maintains proper security posture:
- No external LoadBalancer services
- No Ingress resources
- No public IPs on GKE nodes
- No external forwarding rules
- Firewall rules are in place
"""

import subprocess
from typing import Optional
from kubernetes import client, config


class SecurityPostureChecker:
    """Checks security posture of the multi-cluster setup."""

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
            return client.CoreV1Api(), client.NetworkingV1Api()
        except Exception as e:
            self._log(f"Failed to load kubeconfig for context {context}: {e}")
            raise

    def _run_gcloud(self, args: list) -> tuple[bool, str]:
        """Run a gcloud command and return success status and output."""
        cmd = ["gcloud"] + args
        if self.project_id:
            cmd.extend(["--project", self.project_id])

        self._log(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def check_no_external_lb_services(self) -> list:
        """Check that no services have external LoadBalancer IPs."""
        results = []

        for cluster_name, cluster_cfg in self.cfg.get('clusters', {}).items():
            context = cluster_cfg.get('context', f"gke-{cluster_name}")
            namespace = cluster_cfg.get('namespace', 'bank-of-anthos')

            try:
                core_api, _ = self._get_k8s_client(context)
                services = core_api.list_namespaced_service(namespace=namespace)

                external_lbs = []
                for svc in services.items:
                    if svc.spec.type == "LoadBalancer":
                        # Check if it has an external IP
                        if svc.status.load_balancer.ingress:
                            for ingress in svc.status.load_balancer.ingress:
                                ip = ingress.ip
                                # Check if it's an internal IP (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
                                if ip and not (ip.startswith('10.') or
                                              ip.startswith('172.') or
                                              ip.startswith('192.168.')):
                                    external_lbs.append(f"{svc.metadata.name}={ip}")

                if external_lbs:
                    results.append({
                        'name': f"No external LB services ({cluster_name})",
                        'passed': False,
                        'details': f"Found external IPs: {', '.join(external_lbs)}"
                    })
                else:
                    results.append({
                        'name': f"No external LB services ({cluster_name})",
                        'passed': True,
                        'details': "All LoadBalancer services are internal"
                    })

            except Exception as e:
                self._log(f"Error checking services in {cluster_name}: {e}")
                results.append({
                    'name': f"No external LB services ({cluster_name})",
                    'passed': False,
                    'details': str(e)
                })

        return results

    def check_no_ingress_resources(self) -> list:
        """Check that no Ingress resources exist."""
        results = []

        for cluster_name, cluster_cfg in self.cfg.get('clusters', {}).items():
            context = cluster_cfg.get('context', f"gke-{cluster_name}")
            namespace = cluster_cfg.get('namespace', 'bank-of-anthos')

            try:
                _, networking_api = self._get_k8s_client(context)
                ingresses = networking_api.list_namespaced_ingress(namespace=namespace)

                if ingresses.items:
                    ingress_names = [ing.metadata.name for ing in ingresses.items]
                    results.append({
                        'name': f"No Ingress resources ({cluster_name})",
                        'passed': False,
                        'details': f"Found: {', '.join(ingress_names)}"
                    })
                else:
                    results.append({
                        'name': f"No Ingress resources ({cluster_name})",
                        'passed': True,
                        'details': "No Ingress resources found"
                    })

            except Exception as e:
                self._log(f"Error checking ingresses in {cluster_name}: {e}")
                results.append({
                    'name': f"No Ingress resources ({cluster_name})",
                    'passed': False,
                    'details': str(e)
                })

        return results

    def check_private_nodes(self) -> list:
        """Check that GKE nodes have no public IPs."""
        results = []

        if not self.project_id:
            results.append({
                'name': "GKE nodes have private IPs only",
                'passed': False,
                'details': "Project ID required for this check"
            })
            return results

        success, output = self._run_gcloud([
            "compute", "instances", "list",
            "--filter", "name~gke",
            "--format", "value(name,networkInterfaces[0].accessConfigs[0].natIP)"
        ])

        if not success:
            results.append({
                'name': "GKE nodes have private IPs only",
                'passed': False,
                'details': f"Failed to list instances: {output}"
            })
            return results

        # Parse output - each line is "instance-name\tnat-ip" (nat-ip is empty if private)
        public_nodes = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2 and parts[1]:
                    public_nodes.append(f"{parts[0]}={parts[1]}")

        if public_nodes:
            results.append({
                'name': "GKE nodes have private IPs only",
                'passed': False,
                'details': f"Nodes with public IPs: {', '.join(public_nodes)}"
            })
        else:
            results.append({
                'name': "GKE nodes have private IPs only",
                'passed': True,
                'details': "All GKE nodes are private"
            })

        return results

    def check_no_external_forwarding_rules(self) -> list:
        """Check that no external forwarding rules exist."""
        results = []

        if not self.project_id:
            results.append({
                'name': "No external forwarding rules",
                'passed': False,
                'details': "Project ID required for this check"
            })
            return results

        success, output = self._run_gcloud([
            "compute", "forwarding-rules", "list",
            "--filter", "loadBalancingScheme=EXTERNAL",
            "--format", "value(name)"
        ])

        if not success:
            results.append({
                'name': "No external forwarding rules",
                'passed': False,
                'details': f"Failed to list forwarding rules: {output}"
            })
            return results

        external_rules = [r for r in output.strip().split('\n') if r]

        if external_rules:
            results.append({
                'name': "No external forwarding rules",
                'passed': False,
                'details': f"Found: {', '.join(external_rules)}"
            })
        else:
            results.append({
                'name': "No external forwarding rules",
                'passed': True,
                'details': "No external forwarding rules found"
            })

        return results

    def check_firewall_rules_exist(self) -> list:
        """Check that required firewall rules exist."""
        results = []

        if not self.project_id:
            results.append({
                'name': "Required firewall rules exist",
                'passed': False,
                'details': "Project ID required for this check"
            })
            return results

        expected_rules = self.cfg.get('firewall_rules', [])

        for rule_cfg in expected_rules:
            rule_name = rule_cfg['name']

            success, output = self._run_gcloud([
                "compute", "firewall-rules", "describe", rule_name,
                "--format", "value(name,disabled)"
            ])

            if success and output:
                parts = output.strip().split('\t')
                disabled = len(parts) > 1 and parts[1].lower() == 'true'

                if disabled:
                    results.append({
                        'name': f"Firewall rule: {rule_name}",
                        'passed': False,
                        'details': "Rule exists but is disabled"
                    })
                else:
                    results.append({
                        'name': f"Firewall rule: {rule_name}",
                        'passed': True,
                        'details': "Rule exists and is enabled"
                    })
            else:
                results.append({
                    'name': f"Firewall rule: {rule_name}",
                    'passed': False,
                    'details': "Rule does not exist"
                })

        return results

    def check_vpc_peering_active(self) -> list:
        """Check that VPC peering is active."""
        results = []

        if not self.project_id:
            results.append({
                'name': "VPC peering is active",
                'passed': False,
                'details': "Project ID required for this check"
            })
            return results

        success, output = self._run_gcloud([
            "compute", "networks", "peerings", "list",
            "--network", "vpc-c1",
            "--format", "value(name,state)"
        ])

        if not success:
            results.append({
                'name': "VPC peering is active",
                'passed': False,
                'details': f"Failed to list peerings: {output}"
            })
            return results

        active_peerings = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    name, state = parts[0], parts[1]
                    if state == "ACTIVE":
                        active_peerings.append(name)

        if active_peerings:
            results.append({
                'name': "VPC peering is active",
                'passed': True,
                'details': f"Active peerings: {', '.join(active_peerings)}"
            })
        else:
            results.append({
                'name': "VPC peering is active",
                'passed': False,
                'details': "No active VPC peerings found"
            })

        return results

    def run_checks(self) -> list:
        """Run all security posture checks."""
        self.results = []

        # Run all checks
        self.results.extend(self.check_no_external_lb_services())
        self.results.extend(self.check_no_ingress_resources())
        self.results.extend(self.check_private_nodes())
        self.results.extend(self.check_no_external_forwarding_rules())
        self.results.extend(self.check_firewall_rules_exist())
        self.results.extend(self.check_vpc_peering_active())

        return self.results
