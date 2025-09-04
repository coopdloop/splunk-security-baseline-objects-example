"""Simple template engine for dashboard generation."""

import re
from typing import Dict, Any, Union


def render_template(template_str: str, context: Dict[str, Any]) -> str:
    """Render template with Handlebars-like syntax.
    
    Supports:
    - Variables: {{variable}}
    - Array iteration: {{#each array}}...{{/each}}
    - Conditionals: {{#if condition}}...{{/if}}
    - Filters: {{variable|filter}}
    """
    result = template_str
    
    # Handle {{#each}} blocks first (may be nested)
    result = _handle_each_blocks(result, context)
    
    # Handle {{#if}} blocks
    result = _handle_if_blocks(result, context)
    
    # Handle {{#unless}} blocks (opposite of if)
    result = _handle_unless_blocks(result, context)
    
    # Replace simple variables
    result = _replace_variables(result, context)
    
    return result


def _handle_each_blocks(template: str, context: Dict[str, Any]) -> str:
    """Handle {{#each array}}...{{/each}} blocks."""
    pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{\/each\}\}'
    
    def replace_each(match):
        array_name = match.group(1)
        block_content = match.group(2)
        
        if array_name not in context:
            return ""
        
        array_data = context[array_name]
        if not isinstance(array_data, list):
            return str(array_data) if array_data else ""
        
        result = []
        for i, item in enumerate(array_data):
            # Create new context for this iteration
            item_context = context.copy()
            item_context['this'] = item
            item_context['@index'] = i
            item_context['@first'] = i == 0
            item_context['@last'] = i == len(array_data) - 1
            
            # Recursively render the block content
            rendered_block = render_template(block_content, item_context)
            result.append(rendered_block)
        
        return ''.join(result)
    
    # Handle nested each blocks by processing from inside out
    while re.search(pattern, template, flags=re.DOTALL):
        template = re.sub(pattern, replace_each, template, flags=re.DOTALL)
    
    return template


def _handle_if_blocks(template: str, context: Dict[str, Any]) -> str:
    """Handle {{#if condition}}...{{/if}} blocks."""
    pattern = r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{\/if\}\}'
    
    def replace_if(match):
        condition = match.group(1).strip()
        block_content = match.group(2)
        
        # Evaluate condition
        if _evaluate_condition(condition, context):
            return render_template(block_content, context)
        return ""
    
    return re.sub(pattern, replace_if, template, flags=re.DOTALL)


def _handle_unless_blocks(template: str, context: Dict[str, Any]) -> str:
    """Handle {{#unless condition}}...{{/unless}} blocks."""
    pattern = r'\{\{#unless\s+([^}]+)\}\}(.*?)\{\{\/unless\}\}'
    
    def replace_unless(match):
        condition = match.group(1).strip()
        block_content = match.group(2)
        
        # Evaluate condition (opposite of if)
        if not _evaluate_condition(condition, context):
            return render_template(block_content, context)
        return ""
    
    return re.sub(pattern, replace_unless, template, flags=re.DOTALL)


def _evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """Evaluate a simple condition."""
    # Handle @last, @first special variables
    if condition in context:
        value = context[condition]
        return bool(value) and value != 0 and value != ""
    
    # Handle simple existence checks
    return condition in context and context[condition] is not None


def _replace_variables(template: str, context: Dict[str, Any]) -> str:
    """Replace simple variables and apply filters."""
    def replace_var(match):
        var_expression = match.group(1).strip()
        
        # Handle filters: {{variable|filter}}
        if '|' in var_expression:
            var_path, filter_name = var_expression.split('|', 1)
            value = _get_nested_value(context, var_path.strip())
            return _apply_filter(value, filter_name.strip())
        
        # Handle simple variables
        return str(_get_nested_value(context, var_expression))
    
    return re.sub(r'\{\{([^}#\/]+)\}\}', replace_var, template)


def _get_nested_value(context: Dict[str, Any], path: str) -> Any:
    """Get nested value from context using dot notation."""
    keys = path.split('.')
    value = context
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return ""  # Return empty string for missing values
    
    return value


def _apply_filter(value: Any, filter_expr: str) -> str:
    """Apply filters to values."""
    filter_name = filter_expr.strip()
    
    if filter_name == 'title':
        return str(value).title()
    elif filter_name == 'upper':
        return str(value).upper()
    elif filter_name == 'lower':
        return str(value).lower()
    elif filter_name == 'length':
        return str(len(value)) if hasattr(value, '__len__') else "0"
    elif filter_name.startswith("replace '"):
        # Handle replace filter: {{value|replace 'old' 'new'}}
        match = re.match(r"replace '([^']*)'(?: '([^']*)')?", filter_name)
        if match:
            old_val = match.group(1)
            new_val = match.group(2) or ""
            return str(value).replace(old_val, new_val)
    elif filter_name == 'json':
        import json
        return json.dumps(value)
    
    # Unknown filter, return value as-is
    return str(value)