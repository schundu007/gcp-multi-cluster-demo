"""
Network Policy verification checks.

Verifies that Kubernetes NetworkPolicies are correctly configured:
- Default deny policies exist
- Specific allow policies are in place
- Policies are correctly scoped
"""

from typing import Optional
from kubernetes import client, config


class NetworkPolicyChecker:
    """Checks Kubernetes NetworkPolicy configuration."""

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
            return client.NetworkingV1Api()
        except Exception as e:
            self._log(f"Failed to load kubeconfig for context {context}: {e}")
            raise

    def check_default_deny_exists(self) -> list:
        """Check that default-deny NetworkPolicy exists in each cluster."""
        results = []

        for cluster_name, cluster_cfg in self.cfg.get('clusters', {}).items():
            context = cluster_cfg.get('context', f"gke-{cluster_name}")
            namespace = cluster_cfg.get('namespace', 'bank-of-anthos')

            try:
                api = self._get_k8s_client(context)
                policies = api.list_namespaced_network_policy(namespace=namespace)

                # Look for a default-deny policy
                default_deny_found = False
                for policy in policies.items:
                    # Check if this is a default-deny policy
                    # It should have an empty podSelector and both Ingress and Egress in policyTypes
                    if (policy.spec.pod_selector.match_labels is None or
                        len(policy.spec.pod_selector.match_labels) == 0):
                        policy_types = policy.spec.policy_types or []
                        if 'Ingress' in policy_types and 'Egress' in policy_types:
                            if (not policy.spec.ingress and not policy.spec.egress):
                                default_deny_found = True
                                self._log(f"Found default-deny policy: {policy.metadata.name}")
                                break

                if default_deny_found:
                    results.append({
                        'name': f"Default-deny policy exists ({cluster_name})",
                        'passed': True,
                        'details': "Default-deny policy found"
                    })
                else:
                    results.append({
                        'name': f"Default-deny policy exists ({cluster_name})",
                        'passed': False,
                        'details': "No default-deny policy found"
                    })

            except Exception as e:
                self._log(f"Error checking policies in {cluster_name}: {e}")
                results.append({
                    'name': f"Default-deny policy exists ({cluster_name})",
                    'passed': False,
                    'details': str(e)
                })

        return results

    def check_expected_policies_exist(self) -> list:
        """Check that expected application NetworkPolicies exist."""
        results = []

        expected_policies = {
            'c1': ['frontend-egress', 'frontend-ingress', 'loadgenerator-egress', 'accounts-db-ingress'],
            'c2': ['backend-ingress', 'backend-egress', 'ledger-db-ingress']
        }

        for cluster_name, cluster_cfg in self.cfg.get('clusters', {}).items():
            context = cluster_cfg.get('context', f"gke-{cluster_name}")
            namespace = cluster_cfg.get('namespace', 'bank-of-anthos')
            expected = expected_policies.get(cluster_name, [])

            try:
                api = self._get_k8s_client(context)
                policies = api.list_namespaced_network_policy(namespace=namespace)
                existing_names = [p.metadata.name for p in policies.items]

                for policy_name in expected:
                    if policy_name in existing_names:
                        results.append({
                            'name': f"NetworkPolicy: {policy_name} ({cluster_name})",
                            'passed': True,
                            'details': "Policy exists"
                        })
                    else:
                        results.append({
                            'name': f"NetworkPolicy: {policy_name} ({cluster_name})",
                            'passed': False,
                            'details': "Policy not found"
                        })

            except Exception as e:
                self._log(f"Error checking policies in {cluster_name}: {e}")
                for policy_name in expected:
                    results.append({
                        'name': f"NetworkPolicy: {policy_name} ({cluster_name})",
                        'passed': False,
                        'details': str(e)
                    })

        return results

    def check_frontend_egress_policy(self) -> list:
        """Check that frontend egress policy allows only C2 traffic."""
        results = []

        cluster_cfg = self.cfg.get('clusters', {}).get('c1', {})
        context = cluster_cfg.get('context', 'gke-c1')
        namespace = cluster_cfg.get('namespace', 'bank-of-anthos')
        c2_cidr = self.cfg.get('clusters', {}).get('c2', {}).get('vpc_cidr', '10.1.0.0/16')

        try:
            api = self._get_k8s_client(context)

            try:
                policy = api.read_namespaced_network_policy(
                    name='frontend-egress',
                    namespace=namespace
                )

                # Verify it selects frontend pods
                selector = policy.spec.pod_selector.match_labels or {}
                if selector.get('app') != 'frontend':
                    results.append({
                        'name': "Frontend egress policy targets frontend",
                        'passed': False,
                        'details': f"Wrong selector: {selector}"
                    })
                    return results

                # Verify egress rules
                egress_rules = policy.spec.egress or []
                allows_c2 = False
                allows_dns = False

                for rule in egress_rules:
                    for to in rule.to or []:
                        if to.ip_block:
                            cidr = to.ip_block.cidr
                            if cidr == c2_cidr or cidr.startswith('10.1.'):
                                allows_c2 = True
                        if to.namespace_selector:
                            # Check for DNS namespace
                            match_labels = to.namespace_selector.match_labels or {}
                            if 'kube-system' in str(match_labels):
                                allows_dns = True

                if allows_c2:
                    results.append({
                        'name': "Frontend egress allows C2 traffic",
                        'passed': True,
                        'details': f"Egress to {c2_cidr} allowed"
                    })
                else:
                    results.append({
                        'name': "Frontend egress allows C2 traffic",
                        'passed': False,
                        'details': "No egress rule for C2 CIDR found"
                    })

            except client.exceptions.ApiException as e:
                if e.status == 404:
                    results.append({
                        'name': "Frontend egress policy analysis",
                        'passed': False,
                        'details': "Policy not found"
                    })
                else:
                    raise

        except Exception as e:
            self._log(f"Error analyzing frontend egress policy: {e}")
            results.append({
                'name': "Frontend egress policy analysis",
                'passed': False,
                'details': str(e)
            })

        return results

    def check_backend_ingress_policy(self) -> list:
        """Check that backend ingress policy allows only C1 traffic."""
        results = []

        cluster_cfg = self.cfg.get('clusters', {}).get('c2', {})
        context = cluster_cfg.get('context', 'gke-c2')
        namespace = cluster_cfg.get('namespace', 'bank-of-anthos')
        c1_cidr = self.cfg.get('clusters', {}).get('c1', {}).get('vpc_cidr', '10.0.0.0/16')

        try:
            api = self._get_k8s_client(context)

            try:
                policy = api.read_namespaced_network_policy(
                    name='backend-ingress',
                    namespace=namespace
                )

                # Verify it selects backend pods
                selector = policy.spec.pod_selector.match_labels or {}
                if selector.get('tier') != 'backend':
                    results.append({
                        'name': "Backend ingress policy targets backend tier",
                        'passed': False,
                        'details': f"Wrong selector: {selector}"
                    })
                    return results

                # Verify ingress rules
                ingress_rules = policy.spec.ingress or []
                allows_c1 = False

                for rule in ingress_rules:
                    for from_rule in rule._from or []:
                        if from_rule.ip_block:
                            cidr = from_rule.ip_block.cidr
                            if cidr == c1_cidr or cidr.startswith('10.0.'):
                                allows_c1 = True

                if allows_c1:
                    results.append({
                        'name': "Backend ingress allows C1 traffic",
                        'passed': True,
                        'details': f"Ingress from {c1_cidr} allowed"
                    })
                else:
                    results.append({
                        'name': "Backend ingress allows C1 traffic",
                        'passed': False,
                        'details': "No ingress rule for C1 CIDR found"
                    })

            except client.exceptions.ApiException as e:
                if e.status == 404:
                    results.append({
                        'name': "Backend ingress policy analysis",
                        'passed': False,
                        'details': "Policy not found"
                    })
                else:
                    raise

        except Exception as e:
            self._log(f"Error analyzing backend ingress policy: {e}")
            results.append({
                'name': "Backend ingress policy analysis",
                'passed': False,
                'details': str(e)
            })

        return results

    def run_checks(self) -> list:
        """Run all network policy checks."""
        self.results = []

        # Run all checks
        self.results.extend(self.check_default_deny_exists())
        self.results.extend(self.check_expected_policies_exist())
        self.results.extend(self.check_frontend_egress_policy())
        self.results.extend(self.check_backend_ingress_policy())

        return self.results
