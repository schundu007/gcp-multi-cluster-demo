#!/usr/bin/env python3
"""
Verification tool for GCP Multi-Cluster Networking & Security setup.

This tool verifies:
1. Cross-cluster connectivity (C1 -> C2 and C2 -> C1)
2. Security posture (no external exposure, network policies in place)
3. Infrastructure configuration (firewall rules, VPC peering)
"""

import os
import sys
import yaml
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from checks.connectivity import ConnectivityChecker
from checks.security_posture import SecurityPostureChecker
from checks.network_policy import NetworkPolicyChecker

console = Console()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def print_banner():
    """Print the verification tool banner."""
    console.print("\n[bold blue]" + "=" * 60 + "[/bold blue]")
    console.print("[bold blue]  GCP Multi-Cluster Verification Tool[/bold blue]")
    console.print("[bold blue]" + "=" * 60 + "[/bold blue]\n")


def print_section(title: str):
    """Print a section header."""
    console.print(f"\n[bold cyan]=== {title} ===[/bold cyan]\n")


def print_result(name: str, passed: bool, details: str = ""):
    """Print a test result."""
    status = "[green][PASS][/green]" if passed else "[red][FAIL][/red]"
    detail_str = f" - {details}" if details else ""
    console.print(f"  {status} {name}{detail_str}")


def print_summary(results: list):
    """Print the summary of all tests."""
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed

    console.print("\n[bold]=== Summary ===[/bold]")

    table = Table(show_header=False, box=None)
    table.add_row("Total checks:", str(total))
    table.add_row("[green]Passed:[/green]", f"[green]{passed}[/green]")
    table.add_row("[red]Failed:[/red]", f"[red]{failed}[/red]")
    console.print(table)

    if failed == 0:
        console.print("\n[bold green]All checks passed![/bold green]\n")
    else:
        console.print(f"\n[bold red]{failed} check(s) failed. See details above.[/bold red]\n")

    return failed == 0


@click.command()
@click.option('--config', '-c', default='config.yaml',
              help='Path to configuration file')
@click.option('--project-id', '-p', envvar='PROJECT_ID',
              help='GCP Project ID')
@click.option('--connectivity', is_flag=True,
              help='Run connectivity tests only')
@click.option('--security', is_flag=True,
              help='Run security posture tests only')
@click.option('--network-policy', is_flag=True,
              help='Run network policy tests only')
@click.option('--all', '-a', 'run_all', is_flag=True,
              help='Run all tests')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def main(config, project_id, connectivity, security, network_policy, run_all, verbose):
    """
    Verify GCP Multi-Cluster networking and security configuration.

    Examples:
        python verify.py --all --project-id=my-project
        python verify.py --connectivity
        python verify.py --security --verbose
    """
    print_banner()

    # Load configuration
    config_path = Path(__file__).parent / config
    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        sys.exit(1)

    cfg = load_config(config_path)

    # Determine which tests to run
    if not any([connectivity, security, network_policy, run_all]):
        run_all = True

    all_results = []

    # Run connectivity tests
    if run_all or connectivity:
        print_section("Connectivity Tests")
        try:
            checker = ConnectivityChecker(cfg, project_id, verbose)
            results = checker.run_checks()
            all_results.extend(results)
            for r in results:
                print_result(r['name'], r['passed'], r.get('details', ''))
        except Exception as e:
            console.print(f"[red]Error running connectivity tests: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()

    # Run security posture tests
    if run_all or security:
        print_section("Security Posture Tests")
        try:
            checker = SecurityPostureChecker(cfg, project_id, verbose)
            results = checker.run_checks()
            all_results.extend(results)
            for r in results:
                print_result(r['name'], r['passed'], r.get('details', ''))
        except Exception as e:
            console.print(f"[red]Error running security tests: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()

    # Run network policy tests
    if run_all or network_policy:
        print_section("Network Policy Tests")
        try:
            checker = NetworkPolicyChecker(cfg, project_id, verbose)
            results = checker.run_checks()
            all_results.extend(results)
            for r in results:
                print_result(r['name'], r['passed'], r.get('details', ''))
        except Exception as e:
            console.print(f"[red]Error running network policy tests: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()

    # Print summary
    success = print_summary(all_results)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
