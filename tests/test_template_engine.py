"""Tests for template engine."""

import pytest
from splunk_ta_repo.template_engine import render_template


def test_simple_variable_substitution():
    """Test basic variable substitution."""
    template = "Hello {{name}}!"
    context = {"name": "World"}
    result = render_template(template, context)
    assert result == "Hello World!"


def test_nested_variable():
    """Test nested variable access."""
    template = "{{user.name}} lives in {{user.city}}"
    context = {
        "user": {
            "name": "John",
            "city": "New York"
        }
    }
    result = render_template(template, context)
    assert result == "John lives in New York"


def test_array_iteration():
    """Test array iteration with {{#each}}."""
    template = "{{#each items}}{{this}} {{/each}}"
    context = {"items": ["apple", "banana", "cherry"]}
    result = render_template(template, context)
    assert result == "apple banana cherry "


def test_array_iteration_with_context():
    """Test array iteration with index and conditional variables."""
    template = "{{#each items}}{{@index}}: {{this}}{{#unless @last}}, {{/unless}}{{/each}}"
    context = {"items": ["a", "b", "c"]}
    result = render_template(template, context)
    assert result == "0: a, 1: b, 2: c"


def test_conditional_if():
    """Test conditional {{#if}} blocks."""
    template = "{{#if show_message}}Hello World!{{/if}}"
    
    context = {"show_message": True}
    result = render_template(template, context)
    assert result == "Hello World!"
    
    context = {"show_message": False}
    result = render_template(template, context)
    assert result == ""


def test_conditional_unless():
    """Test conditional {{#unless}} blocks."""
    template = "{{#unless hide_message}}Hello World!{{/unless}}"
    
    context = {"hide_message": False}
    result = render_template(template, context)
    assert result == "Hello World!"
    
    context = {"hide_message": True}
    result = render_template(template, context)
    assert result == ""


def test_filters():
    """Test variable filters."""
    template = "{{name|title}} {{name|upper}} {{name|lower}}"
    context = {"name": "john doe"}
    result = render_template(template, context)
    assert result == "John Doe JOHN DOE john doe"


def test_replace_filter():
    """Test replace filter."""
    template = "{{text|replace 'old' 'new'}}"
    context = {"text": "This is old text"}
    result = render_template(template, context)
    assert result == "This is new text"


def test_complex_template():
    """Test complex template with multiple features."""
    template = """
{{#if enable_section}}
Title: {{title|title}}
Indexes: {{#each indexes}}"{{this}}"{{#unless @last}}, {{/unless}}{{/each}}
{{/if}}
""".strip()
    
    context = {
        "enable_section": True,
        "title": "security dashboard",
        "indexes": ["security", "firewall", "ids"]
    }
    
    result = render_template(template, context)
    expected = 'Title: Security Dashboard\nIndexes: "security", "firewall", "ids"'
    assert result == expected


def test_missing_variable():
    """Test handling of missing variables."""
    template = "Hello {{missing_var}}!"
    context = {}
    result = render_template(template, context)
    assert result == "Hello !"


def test_dashboard_template_example():
    """Test a realistic dashboard template example."""
    template = '''
{
  "title": "{{dashboard_title}}",
  "query": "index IN ({{#each indexes}}\\"{{this}}\\"{{#unless @last}},{{/unless}}{{/each}}) {{#if severity_filter}}severity={{severity_filter}}{{/if}}"
}
'''.strip()
    
    context = {
        "dashboard_title": "Production Security Dashboard",
        "indexes": ["security", "firewall"],
        "severity_filter": "high"
    }
    
    result = render_template(template, context)
    
    # Should be valid JSON
    import json
    parsed = json.loads(result)
    
    assert parsed["title"] == "Production Security Dashboard"
    assert 'index IN ("security","firewall")' in parsed["query"]
    assert "severity=high" in parsed["query"]