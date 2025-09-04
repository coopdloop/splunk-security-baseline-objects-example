"""Tests for dashboard generator."""

import pytest
import json
import tempfile
from pathlib import Path

from splunk_ta_repo.dashboard_generator import DashboardGenerator
from splunk_ta_repo.exceptions import TemplateError, ValidationError


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_root = Path(tmp_dir)
        
        # Create pyproject.toml to mark repo root
        (repo_root / "pyproject.toml").touch()
        
        # Create template directory
        templates_dir = repo_root / "templates" / "dashboard-templates"
        templates_dir.mkdir(parents=True)
        
        # Create a simple test template
        test_template = {
            "template_info": {
                "name": "test_template",
                "title": "Test Template",
                "description": "A test template",
                "version": "1.0.0"
            },
            "parameters": {
                "dashboard_title": {
                    "type": "string",
                    "description": "Dashboard title",
                    "default": "{{ENV_NAME}} Test Dashboard",
                    "required": True
                },
                "primary_index": {
                    "type": "string",
                    "description": "Primary index",
                    "default": "security",
                    "required": True
                }
            },
            "dashboard": {
                "version": "1.1",
                "title": "{{dashboard_title}}",
                "definition": {
                    "type": "absolute_time.earliest_time",
                    "value": "-24h@h"
                },
                "dataSources": {
                    "ds_test": {
                        "type": "ds.search",
                        "options": {
                            "query": "index={{primary_index}} | stats count"
                        }
                    }
                }
            }
        }
        
        with open(templates_dir / "test_template.json", "w") as f:
            json.dump(test_template, f, indent=2)
        
        yield repo_root


def test_discover_templates(temp_repo):
    """Test template discovery."""
    generator = DashboardGenerator(temp_repo)
    templates = generator.discover_templates()
    
    assert "test_template" in templates
    assert templates["test_template"].name == "test_template.json"


def test_load_template(temp_repo):
    """Test template loading."""
    generator = DashboardGenerator(temp_repo)
    template_data = generator.load_template("test_template")
    
    assert template_data["template_info"]["name"] == "test_template"
    assert "parameters" in template_data
    assert "dashboard" in template_data


def test_load_nonexistent_template(temp_repo):
    """Test loading nonexistent template raises error."""
    generator = DashboardGenerator(temp_repo)
    
    with pytest.raises(TemplateError, match="Template 'nonexistent' not found"):
        generator.load_template("nonexistent")


def test_generate_dashboard(temp_repo):
    """Test dashboard generation."""
    generator = DashboardGenerator(temp_repo)
    
    context = {
        "ENV_NAME": "test",
        "dashboard_title": "Test Dashboard",
        "primary_index": "security"
    }
    
    output_dir = temp_repo / "output"
    output_file = generator.generate_dashboard("test_template", context, output_dir)
    
    assert output_file.exists()
    assert output_file.name == "test_dashboard.json"
    
    # Check dashboard content
    with open(output_file) as f:
        dashboard_data = json.load(f)
    
    assert dashboard_data["title"] == "Test Dashboard"
    assert "index=security" in dashboard_data["dataSources"]["ds_test"]["options"]["query"]
    
    # Check metadata file was created
    metadata_file = output_file.with_suffix("") / "_metadata.json"
    metadata_file = output_dir / f"{output_file.stem}_metadata.json"
    assert metadata_file.exists()


def test_parameter_validation(temp_repo):
    """Test parameter validation."""
    generator = DashboardGenerator(temp_repo)
    template_data = generator.load_template("test_template")
    
    # Missing required parameter
    context = {"ENV_NAME": "test"}
    errors = generator.validate_parameters(template_data, context)
    
    # Should pass because required params have defaults
    assert len(errors) == 0
    
    # Type validation
    context = {
        "dashboard_title": "Test",
        "primary_index": 123  # Wrong type but will be converted to string
    }
    errors = generator.validate_parameters(template_data, context)
    assert len(errors) == 0