#!/usr/bin/env python3
"""
Interactive CLI for generating Splunk dashboards from parameterized JSON templates
Usage: python create-dashboard.py [template_name] [--output-dir=path] [--environment=env]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Union

# Handlebars-like template engine replacement
def render_template(template_str: str, context: Dict[str, Any]) -> str:
    """Simple template rendering with {{variable}} syntax"""
    def replace_var(match):
        var_path = match.group(1).strip()
        
        # Handle array iteration: {{#each array}}...{{/each}}
        if var_path.startswith('#each '):
            return match.group(0)  # Let handle_each process this
            
        # Handle conditionals: {{#if condition}}...{{/if}}
        if var_path.startswith('#if ') or var_path == '/if':
            return match.group(0)  # Let handle_conditionals process this
            
        # Handle simple variables with filters: {{variable|filter}}
        if '|' in var_path:
            var_name, filter_name = var_path.split('|', 1)
            value = get_nested_value(context, var_name.strip())
            return apply_filter(value, filter_name.strip())
        
        # Handle simple variables
        return str(get_nested_value(context, var_path))
    
    # Process template
    result = template_str
    
    # Handle {{#each}} blocks first
    result = handle_each_blocks(result, context)
    
    # Handle {{#if}} blocks
    result = handle_if_blocks(result, context)
    
    # Replace simple variables
    result = re.sub(r'\{\{([^}]+)\}\}', replace_var, result)
    
    return result

def get_nested_value(context: Dict[str, Any], path: str) -> Any:
    """Get nested value from context using dot notation"""
    keys = path.split('.')
    value = context
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return f"{{{{missing:{path}}}}}"  # Return placeholder for missing values
    
    return value

def apply_filter(value: Any, filter_name: str) -> str:
    """Apply simple filters to values"""
    if filter_name == 'title':
        return str(value).title()
    elif filter_name == 'upper':
        return str(value).upper()
    elif filter_name == 'lower':
        return str(value).lower()
    elif filter_name.startswith("replace '") and "' ''" in filter_name:
        # Handle replace filter: {{value|replace 'old' 'new'}}
        parts = filter_name.split("'")
        if len(parts) >= 4:
            old, new = parts[1], parts[3]
            return str(value).replace(old, new)
    return str(value)

def handle_each_blocks(template: str, context: Dict[str, Any]) -> str:
    """Handle {{#each array}}...{{/each}} blocks"""
    pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{\/each\}\}'
    
    def replace_each(match):
        array_name = match.group(1)
        block_content = match.group(2)
        
        if array_name not in context:
            return ""
        
        array_data = context[array_name]
        if not isinstance(array_data, list):
            return ""
        
        result = []
        for i, item in enumerate(array_data):
            item_context = context.copy()
            item_context['this'] = item
            item_context['@index'] = i
            item_context['@first'] = i == 0
            item_context['@last'] = i == len(array_data) - 1
            
            rendered_block = render_template(block_content, item_context)
            result.append(rendered_block)
        
        return ''.join(result)
    
    return re.sub(pattern, replace_each, template, flags=re.DOTALL)

def handle_if_blocks(template: str, context: Dict[str, Any]) -> str:
    """Handle {{#if condition}}...{{/if}} blocks (simplified)"""
    pattern = r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{\/if\}\}'
    
    def replace_if(match):
        condition = match.group(1).strip()
        block_content = match.group(2)
        
        # Simple condition evaluation
        if condition in context and context[condition]:
            return render_template(block_content, context)
        return ""
    
    return re.sub(pattern, replace_if, template, flags=re.DOTALL)

class DashboardGenerator:
    """Interactive dashboard generator"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.repo_root = self.script_dir.parent.parent
        self.templates_dir = self.repo_root / "templates" / "dashboard-templates"
        self.available_templates = self._discover_templates()
    
    def _discover_templates(self) -> Dict[str, Path]:
        """Discover available dashboard templates"""
        templates = {}
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.json"):
                templates[template_file.stem] = template_file
        return templates
    
    def list_templates(self) -> None:
        """List available dashboard templates"""
        print("\n🎯 Available Dashboard Templates:")
        print("=" * 50)
        
        for name, path in self.available_templates.items():
            try:
                with open(path, 'r') as f:
                    template_data = json.load(f)
                    info = template_data.get('template_info', {})
                    title = info.get('title', name)
                    description = info.get('description', 'No description available')
                    category = info.get('category', 'general')
                
                print(f"📊 {name}")
                print(f"   Title: {title}")
                print(f"   Category: {category}")
                print(f"   Description: {description}")
                print()
            except Exception as e:
                print(f"❌ {name} (Error loading: {e})")
                print()
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a dashboard template"""
        if template_name not in self.available_templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.available_templates.keys())}")
        
        template_path = self.available_templates[template_name]
        with open(template_path, 'r') as f:
            return json.load(f)
    
    def prompt_for_parameters(self, template_data: Dict[str, Any], environment: str = None) -> Dict[str, Any]:
        """Interactive parameter collection"""
        parameters = template_data.get('parameters', {})
        context = {'ENV_NAME': environment} if environment else {}
        
        print(f"\n🔧 Configuring Parameters for {template_data['template_info']['title']}")
        print("=" * 60)
        
        for param_name, param_config in parameters.items():
            param_type = param_config.get('type', 'string')
            description = param_config.get('description', param_name)
            default_value = param_config.get('default')
            required = param_config.get('required', False)
            
            # Render default value if it contains template variables
            if isinstance(default_value, str) and '{{' in default_value:
                default_value = render_template(default_value, context)
            
            print(f"\n📝 {param_name}")
            print(f"   Description: {description}")
            print(f"   Type: {param_type}")
            if default_value is not None:
                print(f"   Default: {default_value}")
            
            # Get user input based on parameter type
            if param_type == 'array':
                value = self._prompt_array(param_name, default_value, required)
            elif param_type == 'number':
                value = self._prompt_number(param_name, default_value, required)
            elif param_type == 'boolean':
                value = self._prompt_boolean(param_name, default_value, required)
            elif param_type == 'object':
                value = self._prompt_object(param_name, default_value, required)
            else:  # string
                value = self._prompt_string(param_name, default_value, required)
            
            context[param_name] = value
        
        return context
    
    def _prompt_string(self, name: str, default: Any, required: bool) -> str:
        """Prompt for string input"""
        while True:
            if default is not None:
                user_input = input(f"   Enter {name} [{default}]: ").strip()
                if not user_input:
                    return str(default)
            else:
                user_input = input(f"   Enter {name}: ").strip()
            
            if user_input or not required:
                return user_input
            print("   ⚠️  This field is required. Please enter a value.")
    
    def _prompt_number(self, name: str, default: Any, required: bool) -> Union[int, float]:
        """Prompt for numeric input"""
        while True:
            if default is not None:
                user_input = input(f"   Enter {name} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"   Enter {name}: ").strip()
            
            if not user_input and not required:
                return None
            
            try:
                # Try int first, then float
                if '.' in user_input:
                    return float(user_input)
                else:
                    return int(user_input)
            except ValueError:
                print("   ⚠️  Please enter a valid number.")
    
    def _prompt_boolean(self, name: str, default: Any, required: bool) -> bool:
        """Prompt for boolean input"""
        while True:
            default_str = "y" if default else "n"
            user_input = input(f"   {name} (y/n) [{default_str}]: ").strip().lower()
            
            if not user_input:
                return bool(default)
            
            if user_input in ['y', 'yes', 'true', '1']:
                return True
            elif user_input in ['n', 'no', 'false', '0']:
                return False
            else:
                print("   ⚠️  Please enter y/n, yes/no, true/false, or 1/0.")
    
    def _prompt_array(self, name: str, default: Any, required: bool) -> List[str]:
        """Prompt for array input"""
        print(f"   Enter {name} (comma-separated values):")
        
        if default is not None:
            default_str = ", ".join(str(item) for item in default) if isinstance(default, list) else str(default)
            user_input = input(f"   [{default_str}]: ").strip()
            if not user_input:
                return default if isinstance(default, list) else [default]
        else:
            user_input = input(f"   : ").strip()
        
        if not user_input and not required:
            return []
        
        return [item.strip() for item in user_input.split(',') if item.strip()]
    
    def _prompt_object(self, name: str, default: Any, required: bool) -> Dict[str, Any]:
        """Prompt for object input (simplified - just return default for now)"""
        print(f"   Using default value for {name} (object editing not implemented)")
        return default if default is not None else {}
    
    def generate_dashboard(self, template_name: str, context: Dict[str, Any], output_dir: Path) -> Path:
        """Generate dashboard from template and context"""
        template_data = self.load_template(template_name)
        
        # Render the dashboard template
        dashboard_json = json.dumps(template_data['dashboard'], indent=2)
        rendered_dashboard = render_template(dashboard_json, context)
        
        try:
            dashboard_data = json.loads(rendered_dashboard)
        except json.JSONDecodeError as e:
            print(f"❌ Error rendering template: {e}")
            print("Rendered content preview:")
            print(rendered_dashboard[:500] + "..." if len(rendered_dashboard) > 500 else rendered_dashboard)
            raise
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        dashboard_title = context.get('dashboard_title', template_name)
        safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', dashboard_title.lower())
        output_file = output_dir / f"{safe_filename}.json"
        
        # Write dashboard
        with open(output_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        # Create metadata file
        metadata = {
            'template_used': template_name,
            'generated_at': datetime.now().isoformat(),
            'parameters': context,
            'splunk_version': '9.0+',
            'dashboard_type': 'splunk_dashboard_studio'
        }
        
        metadata_file = output_dir / f"{safe_filename}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_file
    
    def interactive_mode(self, template_name: str = None, environment: str = None, output_dir: str = None) -> None:
        """Run interactive dashboard generation"""
        print("🚀 Splunk Dashboard Generator")
        print("=" * 40)
        
        # Select template
        if not template_name:
            self.list_templates()
            template_name = input("\n📋 Enter template name: ").strip()
        
        if template_name not in self.available_templates:
            print(f"❌ Template '{template_name}' not found.")
            return
        
        # Load template
        try:
            template_data = self.load_template(template_name)
        except Exception as e:
            print(f"❌ Error loading template: {e}")
            return
        
        # Get environment if not provided
        if not environment:
            environment = input("🏢 Enter environment name (optional): ").strip() or None
        
        # Get output directory
        if not output_dir:
            environments_dir = self.repo_root / "environments"
            if environment and (environments_dir / environment).exists():
                default_dir = f"environments/{environment}/dashboards/generated"
            else:
                default_dir = "dashboards/generated"
            
            output_dir = input(f"📁 Output directory [{default_dir}]: ").strip() or default_dir
        
        output_path = self.repo_root / output_dir
        
        # Collect parameters
        try:
            context = self.prompt_for_parameters(template_data, environment)
        except KeyboardInterrupt:
            print("\n\n🚫 Generation cancelled by user.")
            return
        
        # Generate dashboard
        try:
            print(f"\n🔨 Generating dashboard...")
            output_file = self.generate_dashboard(template_name, context, output_path)
            
            print(f"\n✅ Dashboard generated successfully!")
            print(f"📄 Dashboard: {output_file}")
            print(f"📋 Metadata: {output_file.with_suffix('')}_metadata.json")
            
            # Provide next steps
            print(f"\n📖 Next Steps:")
            print(f"1. Import the dashboard JSON into Splunk Dashboard Studio")
            print(f"2. Verify all searches execute correctly")
            print(f"3. Customize visualizations as needed")
            print(f"4. Test with your environment's data")
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            return

def main():
    parser = argparse.ArgumentParser(description='Generate Splunk dashboards from templates')
    parser.add_argument('template', nargs='?', help='Template name to use')
    parser.add_argument('--output-dir', help='Output directory for generated dashboard')
    parser.add_argument('--environment', help='Environment name for parameter defaults')
    parser.add_argument('--list', action='store_true', help='List available templates')
    
    args = parser.parse_args()
    
    generator = DashboardGenerator()
    
    if args.list:
        generator.list_templates()
        return
    
    try:
        generator.interactive_mode(args.template, args.environment, args.output_dir)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()