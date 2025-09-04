"""Template validation utilities that handle Handlebars syntax."""

import json
import re
from typing import Dict, Any, List, Tuple


def validate_template_structure(template_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """Validate template structure, returning (errors, warnings)."""
    errors = []
    warnings = []
    
    # Check required sections (handle both formats)
    required_sections = ['template_info']
    for section in required_sections:
        if section not in template_data:
            errors.append(f"Missing required section: {section}")
    
    # Check for dashboard content (either format)
    if 'dashboard' not in template_data and 'dashboard_template_raw' not in template_data:
        errors.append("Missing dashboard content")
    
    # Validate template_info
    if 'template_info' in template_data:
        info = template_data['template_info']
        required_info_fields = ['name', 'title', 'description']
        
        for field in required_info_fields:
            if field not in info:
                errors.append(f"template_info missing required field: {field}")
    
    # Validate parameters section
    if 'parameters' in template_data:
        parameters = template_data['parameters']
        if not isinstance(parameters, dict):
            errors.append("parameters section must be an object")
        else:
            for param_name, param_config in parameters.items():
                if not isinstance(param_config, dict):
                    warnings.append(f"Parameter '{param_name}' configuration is not an object")
                    continue
                
                # Check parameter configuration
                if 'type' not in param_config:
                    warnings.append(f"Parameter '{param_name}' missing type specification")
                
                if param_config.get('required', False) and 'default' not in param_config:
                    warnings.append(f"Required parameter '{param_name}' has no default value")
    
    return errors, warnings


def validate_template_syntax(template_str: str, strict: bool = False) -> Tuple[List[str], List[str]]:
    """Enhanced Handlebars template syntax validation."""
    errors = []
    warnings = []
    
    # Check for unmatched braces
    open_braces = template_str.count('{{')
    close_braces = template_str.count('}}')
    
    if open_braces != close_braces:
        errors.append(f"Unmatched template braces: {open_braces} opening vs {close_braces} closing")
    
    # Enhanced block helper validation
    block_helpers = ['each', 'if', 'unless', 'with']
    for helper in block_helpers:
        opens = len(re.findall(fr'\{{\#{helper}\s', template_str))
        closes = len(re.findall(r'\{\{\/' + helper + r'\}\}', template_str))
        if opens != closes:
            errors.append(f"Unmatched #{helper} blocks: {opens} opens, {closes} closes")
    
    # Check for problematic patterns
    problematic_patterns = [
        (r'\{\{\{[^}]*\}\}\}', 'Triple braces found - use double braces for JSON templates'),
        (r'\{\{[^}]*\n[^}]*\}\}', 'Multi-line template expressions may cause JSON parsing issues'),
        (r'\{\{[^}]*"[^}]*\}\}', 'Template expressions containing quotes may break JSON'),
    ]
    
    for pattern, message in problematic_patterns:
        if re.search(pattern, template_str, re.MULTILINE):
            warnings.append(message)
    
    # Strict mode additional checks
    if strict:
        # Check for performance issues
        complex_queries = re.findall(r'index=[^|]*\|.*?\|.*?\|', template_str)
        if len(complex_queries) > 10:
            warnings.append(f"Found {len(complex_queries)} complex queries - consider simplifying for performance")
        
        # Check for security patterns
        if re.search(r'\*\s*\|', template_str):
            warnings.append("Wildcard searches found - ensure appropriate time bounds for security")
        
        # Check for deprecated Splunk syntax
        deprecated_patterns = [
            (r'transaction\s+', 'Consider using stats instead of transaction for better performance'),
            (r'join\s+', 'Consider using stats instead of join for better performance'),
        ]
        
        for pattern, message in deprecated_patterns:
            if re.search(pattern, template_str, re.IGNORECASE):
                warnings.append(message)
    
    return errors, warnings


def create_test_context(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive test context for template validation."""
    parameters = template_data.get('parameters', {})
    
    # Start with comprehensive base context
    context = {
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
    }
    
    # Override with template-specific parameters
    for param_name, param_config in parameters.items():
        param_type = param_config.get('type', 'string')
        default_value = param_config.get('default')
        
        if default_value is not None:
            context[param_name] = default_value
        elif param_name not in context:  # Don't override comprehensive defaults
            # Create sample values based on type
            if param_type == 'string':
                context[param_name] = f'sample_{param_name}'
            elif param_type == 'number':
                context[param_name] = 42
            elif param_type == 'boolean':
                context[param_name] = True
            elif param_type == 'array':
                context[param_name] = ['item1', 'item2', 'item3']
            elif param_type == 'object':
                context[param_name] = {'key': 'value'}
            else:
                context[param_name] = f'unknown_type_{param_name}'
    
    return context


def validate_template_rendering(template_data: Dict[str, Any], strict: bool = False) -> Tuple[List[str], List[str]]:
    """Enhanced template rendering validation with performance checks."""
    errors = []
    warnings = []
    
    try:
        from .template_engine import render_template
        import time
        
        # Create test context
        context = create_test_context(template_data)
        
        # Test rendering the dashboard section
        if 'dashboard' in template_data:
            dashboard_json = json.dumps(template_data['dashboard'], indent=2)
            
            # Performance timing
            start_time = time.time()
            rendered = render_template(dashboard_json, context)
            render_time = time.time() - start_time
            
            # Performance warnings
            if render_time > 1.0:
                warnings.append(f"Template rendering took {render_time:.2f}s - consider optimizing")
            
            # Validate JSON structure
            try:
                parsed_json = json.loads(rendered)
                
                # Enhanced validation checks
                if strict:
                    # Check for large dashboard structures
                    json_size = len(rendered)
                    if json_size > 100000:  # 100KB
                        warnings.append(f"Large dashboard size ({json_size} bytes) - may impact Splunk performance")
                    
                    # Validate Splunk-specific structure
                    validate_splunk_dashboard_structure(parsed_json, errors, warnings)
                    
            except json.JSONDecodeError as e:
                errors.append(f"Template rendering produces invalid JSON: {e}")
        
    except Exception as e:
        errors.append(f"Template rendering failed: {e}")
    
    return errors, warnings


def validate_splunk_dashboard_structure(dashboard: Dict[str, Any], errors: List[str], warnings: List[str]):
    """Validate Splunk Dashboard Studio specific structure."""
    required_fields = ['version', 'title']
    for field in required_fields:
        if field not in dashboard:
            warnings.append(f"Dashboard missing recommended field: {field}")
    
    # Check for valid version
    if 'version' in dashboard and dashboard['version'] not in ['1.0', '1.1', '1.2']:
        warnings.append(f"Unknown dashboard version: {dashboard['version']}")
    
    # Validate dataSources structure
    if 'dataSources' in dashboard:
        for ds_name, ds_config in dashboard['dataSources'].items():
            if 'type' not in ds_config:
                errors.append(f"DataSource '{ds_name}' missing type field")
            elif ds_config['type'] not in ['ds.search', 'ds.chain', 'ds.savedSearch']:
                warnings.append(f"DataSource '{ds_name}' has unusual type: {ds_config['type']}")
    
    # Validate visualizations
    if 'visualizations' in dashboard:
        for viz_name, viz_config in dashboard['visualizations'].items():
            if 'type' not in viz_config:
                errors.append(f"Visualization '{viz_name}' missing type field")
            
            # Check for valid visualization types
            valid_viz_types = [
                'splunk.singlevalue', 'splunk.line', 'splunk.column', 'splunk.pie',
                'splunk.table', 'splunk.scatter', 'splunk.bubble', 'splunk.area'
            ]
            if viz_config.get('type') not in valid_viz_types:
                warnings.append(f"Visualization '{viz_name}' uses non-standard type: {viz_config.get('type')}")