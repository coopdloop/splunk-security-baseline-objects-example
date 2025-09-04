"""Dashboard generator with template support."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .template_engine import render_template
from .exceptions import TemplateError, ValidationError


class DashboardGenerator:
    """Generate Splunk dashboards from parameterized templates."""
    
    def __init__(self, repo_root: Path = None):
        if repo_root:
            self.repo_root = repo_root
        else:
            # Auto-detect repo root by finding pyproject.toml
            current = Path(__file__).parent
            while current != current.parent:
                if (current / "pyproject.toml").exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                raise TemplateError("Could not find repository root (pyproject.toml not found)")
        
        self.templates_dir = self.repo_root / "templates" / "dashboard-templates"
        
    def discover_templates(self) -> Dict[str, Path]:
        """Discover available dashboard templates."""
        templates = {}
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.json"):
                # Skip metadata and non-template files
                if not template_file.name.endswith("_metadata.json"):
                    templates[template_file.stem] = template_file
        return templates
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load and validate a dashboard template."""
        templates = self.discover_templates()
        
        if template_name not in templates:
            available = list(templates.keys())
            raise TemplateError(
                f"Template '{template_name}' not found. "
                f"Available templates: {available}"
            )
        
        template_path = templates[template_name]
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON in template {template_name}: {e}")
        except IOError as e:
            raise TemplateError(f"Could not read template {template_name}: {e}")
        
        # Validate template structure
        self._validate_template_structure(template_data, template_name)
        
        return template_data
    
    def _validate_template_structure(self, template_data: Dict[str, Any], template_name: str):
        """Validate that template has required structure."""
        required_sections = ['template_info', 'dashboard']
        
        for section in required_sections:
            if section not in template_data:
                raise ValidationError(
                    f"Template '{template_name}' missing required section: {section}"
                )
        
        # Validate template_info
        info = template_data['template_info']
        required_info_fields = ['name', 'title', 'description']
        
        for field in required_info_fields:
            if field not in info:
                raise ValidationError(
                    f"Template '{template_name}' template_info missing: {field}"
                )
    
    def validate_parameters(self, template_data: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Validate that all required parameters are provided."""
        parameters = template_data.get('parameters', {})
        errors = []
        
        for param_name, param_config in parameters.items():
            required = param_config.get('required', False)
            param_type = param_config.get('type', 'string')
            
            if required and param_name not in context:
                errors.append(f"Required parameter '{param_name}' not provided")
                continue
                
            if param_name in context:
                value = context[param_name]
                
                # Type validation
                if param_type == 'number' and not isinstance(value, (int, float)):
                    try:
                        context[param_name] = float(value) if '.' in str(value) else int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Parameter '{param_name}' must be a number")
                
                elif param_type == 'boolean' and not isinstance(value, bool):
                    if isinstance(value, str):
                        context[param_name] = value.lower() in ('true', 'yes', '1', 'on')
                    else:
                        errors.append(f"Parameter '{param_name}' must be a boolean")
                
                elif param_type == 'array' and not isinstance(value, list):
                    if isinstance(value, str):
                        context[param_name] = [item.strip() for item in value.split(',')]
                    else:
                        errors.append(f"Parameter '{param_name}' must be an array")
        
        return errors
    
    def generate_dashboard(self, template_name: str, context: Dict[str, Any], output_dir: Path) -> Path:
        """Generate dashboard from template and context."""
        template_data = self.load_template(template_name)
        
        # Validate parameters
        param_errors = self.validate_parameters(template_data, context)
        if param_errors:
            raise ValidationError(f"Parameter validation failed: {'; '.join(param_errors)}")
        
        # Add default parameters if missing
        parameters = template_data.get('parameters', {})
        for param_name, param_config in parameters.items():
            if param_name not in context and 'default' in param_config:
                default_value = param_config['default']
                # Render default value if it contains template variables
                if isinstance(default_value, str) and '{{' in default_value:
                    default_value = render_template(default_value, context)
                context[param_name] = default_value
        
        # Render dashboard template
        try:
            dashboard_json = json.dumps(template_data['dashboard'], indent=2)
            rendered_dashboard = render_template(dashboard_json, context)
            dashboard_data = json.loads(rendered_dashboard)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Template rendering produced invalid JSON: {e}")
        except Exception as e:
            raise TemplateError(f"Template rendering failed: {e}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        dashboard_title = context.get('dashboard_title', template_name)
        safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', dashboard_title.lower())
        safe_filename = re.sub(r'_+', '_', safe_filename).strip('_')
        
        output_file = output_dir / f"{safe_filename}.json"
        
        # Write dashboard
        with open(output_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        # Create metadata file
        metadata = {
            'template_used': template_name,
            'template_version': template_data['template_info'].get('version', '1.0.0'),
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'splunk-ta-repo dashboard generator',
            'parameters': context,
            'splunk_version': '9.0+',
            'dashboard_type': 'splunk_dashboard_studio'
        }
        
        metadata_file = output_dir / f"{safe_filename}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_file