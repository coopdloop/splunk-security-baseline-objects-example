"""Command-line interface for dashboard generation."""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from typing import Dict, Any, List

from .dashboard_generator import DashboardGenerator
from .exceptions import TemplateError, ValidationError
from .template_validator import validate_template_structure, validate_template_syntax, validate_template_rendering

console = Console()


@click.group()
@click.version_option()
def cli():
    """Splunk TA Repository Dashboard Generator"""
    pass


@cli.command()
def list_templates():
    """List available dashboard templates"""
    generator = DashboardGenerator()
    templates = generator.discover_templates()
    
    if not templates:
        console.print("[red]No templates found![/red]")
        return
    
    table = Table(title="📊 Available Dashboard Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="white")
    
    for name, path in templates.items():
        try:
            # Load template using the proper template loader
            template_data = generator.load_template(name)
            
            info = template_data.get('template_info', {})
            table.add_row(
                name,
                info.get('title', 'N/A'),
                info.get('category', 'general'),
                info.get('description', 'No description')[:50] + "..."
            )
        except json.JSONDecodeError:
            table.add_row(name, "[red]Invalid JSON[/red]", "error", "Template contains syntax errors")
        except Exception as e:
            table.add_row(name, "[red]Error loading[/red]", "error", str(e)[:50])
    
    console.print(table)


@cli.command()
@click.argument('template_name')
@click.option('--environment', '-e', help='Environment name')
@click.option('--output-dir', '-o', help='Output directory')
@click.option('--config-file', '-c', help='Configuration file with parameters')
@click.option('--dry-run', is_flag=True, help='Show what would be generated without creating files')
def generate(template_name: str, environment: str, output_dir: str, config_file: str, dry_run: bool):
    """Generate a dashboard from a template"""
    try:
        generator = DashboardGenerator()
        
        # Load template
        template_data = generator.load_template(template_name)
        info = template_data.get('template_info', {})
        
        console.print(Panel(
            f"[bold cyan]{info.get('title', template_name)}[/bold cyan]\n"
            f"[dim]{info.get('description', 'No description available')}[/dim]",
            title="🎯 Dashboard Template"
        ))
        
        # Load config file or collect parameters interactively
        if config_file:
            with open(config_file, 'r') as f:
                context = json.load(f)
            console.print(f"[green]✓[/green] Loaded parameters from {config_file}")
        else:
            context = collect_parameters_interactive(template_data, environment)
        
        # Determine output directory
        if not output_dir:
            repo_root = generator.repo_root
            if environment and (repo_root / "environments" / environment).exists():
                output_dir = f"environments/{environment}/dashboards/generated"
            else:
                output_dir = "dashboards/generated"
        
        output_path = generator.repo_root / output_dir
        
        if dry_run:
            console.print(Panel(
                f"[yellow]DRY RUN MODE[/yellow]\n"
                f"Template: {template_name}\n"
                f"Environment: {environment or 'None'}\n"
                f"Output: {output_path}\n"
                f"Parameters: {len(context)} configured",
                title="🔍 Preview"
            ))
            return
        
        # Generate dashboard
        console.print(f"[yellow]🔨 Generating dashboard...[/yellow]")
        output_file = generator.generate_dashboard(template_name, context, output_path)
        
        console.print(Panel(
            f"[green]✅ Dashboard generated successfully![/green]\n"
            f"📄 Dashboard: {output_file}\n"
            f"📋 Metadata: {output_file.with_suffix('')}_metadata.json\n\n"
            f"[dim]Next steps:[/dim]\n"
            f"1. Import JSON into Splunk Dashboard Studio\n"
            f"2. Verify searches execute correctly\n"
            f"3. Customize visualizations as needed",
            title="🎉 Success"
        ))
        
    except (TemplateError, ValidationError, FileNotFoundError) as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        raise


def collect_parameters_interactive(template_data: Dict[str, Any], environment: str) -> Dict[str, Any]:
    """Collect parameters interactively with rich prompts"""
    parameters = template_data.get('parameters', {})
    context = {'ENV_NAME': environment} if environment else {}
    
    console.print(Panel(
        f"[bold]Configure Parameters[/bold]\n"
        f"[dim]Press Enter to use default values[/dim]",
        title="🔧 Configuration"
    ))
    
    for param_name, param_config in parameters.items():
        param_type = param_config.get('type', 'string')
        description = param_config.get('description', param_name)
        default_value = param_config.get('default')
        required = param_config.get('required', False)
        
        # Render default value with existing context
        if isinstance(default_value, str) and '{{' in default_value:
            from .template_engine import render_template
            default_value = render_template(default_value, context)
        
        console.print(f"\n[bold cyan]{param_name}[/bold cyan] ({param_type})")
        console.print(f"[dim]{description}[/dim]")
        
        # Collect value based on type
        if param_type == 'string':
            value = Prompt.ask(
                f"Enter {param_name}",
                default=str(default_value) if default_value is not None else None
            )
        elif param_type == 'number':
            if isinstance(default_value, float):
                value = FloatPrompt.ask(
                    f"Enter {param_name}",
                    default=default_value if default_value is not None else None
                )
            else:
                value = IntPrompt.ask(
                    f"Enter {param_name}",
                    default=default_value if default_value is not None else None
                )
        elif param_type == 'boolean':
            value = Confirm.ask(
                f"Enable {param_name}",
                default=bool(default_value) if default_value is not None else None
            )
        elif param_type == 'array':
            default_str = ", ".join(default_value) if default_value else ""
            array_input = Prompt.ask(
                f"Enter {param_name} (comma-separated)",
                default=default_str
            )
            value = [item.strip() for item in array_input.split(',') if item.strip()]
        else:  # object or unknown
            console.print(f"[yellow]Using default for {param_name} (complex type)[/yellow]")
            value = default_value
        
        context[param_name] = value
    
    return context


@cli.command()
@click.argument('template_name')
@click.option('--strict', is_flag=True, help='Enable strict validation mode with performance and security checks')
def validate_template(template_name: str, strict: bool):
    """Validate a dashboard template with optional strict mode"""
    try:
        generator = DashboardGenerator()
        template_data = generator.load_template(template_name)
        
        # Validate template structure
        struct_errors, struct_warnings = validate_template_structure(template_data)
        
        # Enhanced syntax validation with strict mode
        if 'dashboard' in template_data:
            dashboard_json = json.dumps(template_data['dashboard'], indent=2)
            syntax_errors, syntax_warnings = validate_template_syntax(dashboard_json, strict=strict)
        else:
            syntax_errors, syntax_warnings = [], []
        
        # Validate template rendering with strict mode
        render_errors, render_warnings = validate_template_rendering(template_data, strict=strict)
        
        # Combine all validation results
        errors = struct_errors + syntax_errors + render_errors
        warnings = struct_warnings + syntax_warnings + render_warnings
        
        # Show results
        if errors:
            console.print(Panel(
                "\n".join(f"• {error}" for error in errors),
                title="[red]❌ Validation Errors[/red]",
                border_style="red"
            ))
        
        if warnings:
            console.print(Panel(
                "\n".join(f"• {warning}" for warning in warnings),
                title="[yellow]⚠️  Warnings[/yellow]",
                border_style="yellow"
            ))
        
        if not errors and not warnings:
            console.print(Panel(
                "[green]✅ Template validation passed![/green]",
                title="Validation Results"
            ))
        
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise click.ClickException(str(e))


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()