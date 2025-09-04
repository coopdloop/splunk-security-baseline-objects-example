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
        """Discover available dashboard templates (.json and .json.hbs formats)."""
        templates = {}
        if self.templates_dir.exists():
            # Support both .json and .json.hbs/.hbs formats
            for pattern in ["*.json", "*.json.hbs", "*.hbs"]:
                for template_file in self.templates_dir.glob(pattern):
                    # Skip metadata and non-template files
                    if not template_file.name.endswith("_metadata.json"):
                        # Remove .json extension for consistent naming
                        template_name = template_file.stem
                        if template_name.endswith('.json'):
                            template_name = template_name[:-5]  # Remove '.json' 
                        templates[template_name] = template_file
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
                template_content = f.read()
                
            # Try to load as JSON, but handle Handlebars templates more gracefully
            template_data = self._load_template_with_handlebars(template_content, template_name)
        except IOError as e:
            raise TemplateError(f"Could not read template {template_name}: {e}")
        
        # Validate template structure
        self._validate_template_structure(template_data, template_name)
        
        return template_data
    
    def _validate_template_structure(self, template_data: Dict[str, Any], template_name: str):
        """Validate that template has required structure."""
        required_sections = ['template_info']
        
        for section in required_sections:
            if section not in template_data:
                raise ValidationError(
                    f"Template '{template_name}' missing required section: {section}"
                )
        
        # Check for dashboard content (either parsed or raw handlebars)
        if 'dashboard' not in template_data and 'dashboard_template_raw' not in template_data:
            raise ValidationError(
                f"Template '{template_name}' missing dashboard content"
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
        
        # Render dashboard template (handle both formats)
        try:
            if template_data.get('is_handlebars', False):
                # Handle .json.hbs format - render entire template with context
                raw_template = template_data['dashboard_template_raw']
                rendered_content = render_template(raw_template, context)
                full_rendered = json.loads(rendered_content)
                dashboard_data = full_rendered['dashboard']
            else:
                # Handle .json format - dashboard is already parsed
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
    
    def _load_template_with_handlebars(self, template_content: str, template_name: str) -> Dict[str, Any]:
        """Load a template that may contain Handlebars syntax."""
        try:
            # First try to parse as regular JSON
            return json.loads(template_content)
        except json.JSONDecodeError as e:
            # If that fails, it's likely a Handlebars template
            # Store the raw content and mark it as a handlebars template
            try:
                # Validate syntax by rendering with test context
                test_context = self._create_comprehensive_test_context()
                rendered = render_template(template_content, test_context)
                parsed_test = json.loads(rendered)  # Validate structure
                
                # If validation passes, return a structure that preserves the raw template
                return {
                    'template_info': parsed_test.get('template_info', {
                        'name': template_name,
                        'title': f'{template_name.title()} Template',
                        'description': f'Handlebars template: {template_name}'
                    }),
                    'parameters': parsed_test.get('parameters', {}),
                    'dashboard_template_raw': template_content,  # Store raw content
                    'is_handlebars': True  # Flag to indicate template type
                }
                
            except Exception as render_error:
                # If rendering also fails, raise the original JSON error with more context
                raise TemplateError(
                    f"Template {template_name} has invalid syntax. "
                    f"JSON parse error: {e}. "
                    f"Template rendering error: {render_error}"
                )
    
    
    def _create_comprehensive_test_context(self) -> Dict[str, Any]:
        """Create comprehensive test context covering all common template patterns."""
        return {
            # Environment context
            'ENV_NAME': 'test',
            'environment': 'test',
            
            # Dashboard metadata
            'dashboard_title': 'Test Dashboard',
            'dashboard_description': 'Test dashboard for validation',
            
            # Common string parameters
            'primary_index': 'security',
            'streams_index': 'streams',
            'expected_sources_lookup': 'expected_data_sources.csv',
            
            # Array parameters (most common cause of template issues)
            'secondary_indexes': ['firewall', 'ids', 'proxy', 'endpoint'],
            'capture_interfaces': ['eth0', 'eth1', 'bond0'],
            'streams_sourcetypes': ['stream:tcp', 'stream:udp', 'stream:icmp', 'stream:dns', 'stream:http'],
            'data_models_to_validate': ['Authentication', 'Network_Traffic', 'Malware', 'Web', 'Email'],
            'primary_indexes': ['security', 'firewall', 'ids'],
            
            # Numeric parameters
            'ingestion_threshold_gb': 1.0,
            'missing_data_threshold_minutes': 60,
            'compliance_threshold': 85.0,
            'field_population_threshold': 75.0,
            'expected_throughput_mbps': 1000,
            'packet_loss_threshold': 1.0,
            
            # Time parameters
            'time_range_earliest': '-24h@h',
            'time_range_latest': 'now',
            
            # Complex objects (JSON)
            'required_cim_fields': {
                'Authentication': ['user', 'src', 'dest', 'action', 'app'],
                'Network_Traffic': ['src_ip', 'dest_ip', 'src_port', 'dest_port', 'protocol', 'action'],
                'Malware': ['signature', 'file_name', 'file_hash', 'dest', 'vendor_product'],
                'Web': ['url', 'uri_path', 'http_method', 'status', 'src_ip'],
                'Email': ['recipient', 'sender', 'subject', 'action']
            },
            
            # Boolean parameters
            'enable_acceleration': True,
            'strict_validation': False,
            
            # Additional context that might be needed
            'org_name': 'test_org',
            'splunk_version': '9.0+',
            'dashboard_type': 'splunk_dashboard_studio'
        }