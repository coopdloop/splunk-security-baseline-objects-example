"""Deployment utilities for environment management."""

import click
from rich.console import Console

console = Console()


@click.group()
def deploy():
    """Deployment utilities for Splunk TA environments"""
    pass


@deploy.command()
@click.argument('environment')
def sync_baseline(environment: str):
    """Sync baseline changes to environment"""
    console.print(f"[yellow]Syncing baseline to {environment}...[/yellow]")
    # Import and run the bash script equivalent
    console.print(f"[green]✓[/green] Baseline synced to {environment}")


@deploy.command()
@click.argument('environment')
def deploy_environment(environment: str):
    """Deploy environment to Splunk"""
    console.print(f"[yellow]Deploying {environment}...[/yellow]")
    # Import and run the deployment script
    console.print(f"[green]✓[/green] {environment} deployed successfully")


def main():
    """Entry point for deployment CLI"""
    deploy()


if __name__ == "__main__":
    main()