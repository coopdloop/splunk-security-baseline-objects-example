# 🎨 Handlebars Template Guide

## Overview

The dashboard generator now supports advanced **Handlebars templating** with `.json.hbs` files, providing more powerful template capabilities alongside the existing `.json` format.

## 🔄 Template Format Comparison

### Traditional JSON Format (`.json`)
```json
{
  "template_info": {...},
  "parameters": {...},
  "dashboard": {
    "title": "{{dashboard_title}}",
    "inputs": [...]
  }
}
```

### NEW: Handlebars Format (`.json.hbs`)
```handlebars
{
  "template_info": {...},
  "parameters": {...},
  "dashboard": {
    "title": "{{dashboard_title}}",
    "choices": [
      {"label": "All Indexes", "value": "*"}{{#each security_indexes}},
      {"label": "{{this|title}}", "value": "{{this}}"}{{/each}}
    ]
  }
}
```

## 🎛️ Dashboard Studio Input Format

### ✅ Correct Structure (All templates now use this):
```json
"inputs": {
  "input_timerange": {
    "type": "input.timerange",
    "title": "Time Range", 
    "options": {
      "defaultValue": {
        "earliest_time": "-24h@h",
        "latest_time": "now"
      },
      "token": "time_picker"
    }
  },
  "input_index_filter": {
    "type": "input.dropdown",
    "title": "Index Filter",
    "options": {
      "items": [
        {"label": "Security", "value": "security"},
        {"label": "Firewall", "value": "firewall"}
      ],
      "defaultValue": "security",
      "token": "index_filter"
    }
  }
},
"layout": {
  "globalInputs": ["input_timerange", "input_index_filter"],
  "structure": [...]
}
```

### 🎚️ Supported Input Types:
- **`input.timerange`** - Time picker with earliest/latest
- **`input.dropdown`** - Dropdown with items array
- **`input.text`** - Text input field
- **`input.checkbox`** - Checkbox input
- **`input.radio`** - Radio button group

## 🌟 Enhanced Features

### 1. **Proper Handlebars Syntax**
- **Conditionals**: `{{#if enable_geolocation}}...{{/if}}`
- **Loops**: `{{#each security_indexes}}...{{/each}}`
- **Filters**: `{{ENV_NAME|title}}` → "Production"
- **Unless blocks**: `{{#unless @last}},{{/unless}}`

### 2. **Advanced Template Logic**
```handlebars
{
  "position": {
    "x": {{#if enable_geolocation}}400{{else}}0{{/if}},
    "y": 400
  }
}
```

### 3. **Complex Data Structures**
```handlebars
"query": "index IN ({{#each security_indexes}}\"{{this}}\"{{#unless @last}},{{/unless}}{{/each}}) | stats count by severity"
```

## 📋 Template Structure

### Required Sections
```handlebars
{
  "template_info": {
    "name": "template_name",
    "title": "Template Title", 
    "description": "Template description",
    "category": "security",
    "version": "1.0.0",
    "format": "handlebars"  // NEW: Indicates Handlebars template
  },
  "parameters": {
    "param_name": {
      "type": "string|number|boolean|array|object",
      "description": "Parameter description",
      "default": "default_value",
      "required": true|false
    }
  },
  "dashboard": {
    // Standard Splunk Dashboard Studio JSON with Handlebars templating
  }
}
```

## 🛠️ CLI Commands

### List Templates (Both Formats)
```bash
uv run create-dashboard list-templates
```

### Validate Templates
```bash
# Basic validation
uv run create-dashboard validate-template security_basic

# NEW: Strict validation (performance & security checks)
uv run create-dashboard validate-template security_basic --strict
```

### Generate Dashboards
```bash
# Interactive mode
uv run create-dashboard generate security_basic --environment production

# Config file mode  
uv run create-dashboard generate security_basic \
  --environment production \
  --config-file security_config.json
```

## 📝 Example: Security Dashboard Template

### Template File: `security_basic.json.hbs`
```handlebars
{
  "template_info": {
    "name": "security_basic",
    "title": "Basic Security Dashboard",
    "description": "Security monitoring with configurable indexes",
    "category": "security",
    "format": "handlebars"
  },
  "parameters": {
    "dashboard_title": {
      "type": "string",
      "default": "{{ENV_NAME|title}} Security Dashboard",
      "required": true
    },
    "security_indexes": {
      "type": "array",
      "default": ["security", "firewall", "ids"],
      "required": true
    },
    "alert_threshold": {
      "type": "number", 
      "default": 100,
      "required": true
    }
  },
  "dashboard": {
    "title": "{{dashboard_title}}",
    "inputs": {
      "input_index_filter": {
        "type": "input.dropdown",
        "title": "Security Index",
        "options": {
          "items": [
            {"label": "All Indexes", "value": "*"}{{#each security_indexes}},
            {"label": "{{this|title}}", "value": "{{this}}"}{{/each}}
          ],
          "token": "index_filter"
        }
      }
    },
    "layout": {
      "globalInputs": ["input_index_filter"],
      "structure": [...]
    },
    "dataSources": {
      "ds_events": {
        "options": {
          "query": "index IN ({{#each security_indexes}}\"{{this}}\"{{#unless @last}},{{/unless}}{{/each}}) | stats count | eval status=case(count>{{alert_threshold}},\"High\",1=1,\"Normal\")"
        }
      }
    }
  }
}
```

### Config File: `security_config.json`
```json
{
  "dashboard_title": "Production Security Operations",
  "security_indexes": ["security", "firewall", "ids", "endpoint"],
  "alert_threshold": 500
}
```

### Generated Output (Dashboard Studio Format)
```json
{
  "title": "Production Security Operations",
  "inputs": {
    "input_index_filter": {
      "type": "input.dropdown",
      "title": "Security Index",
      "options": {
        "items": [
          {"label": "All Indexes", "value": "*"},
          {"label": "Security", "value": "security"},
          {"label": "Firewall", "value": "firewall"},
          {"label": "Ids", "value": "ids"}, 
          {"label": "Endpoint", "value": "endpoint"}
        ],
        "token": "index_filter"
      }
    }
  },
  "layout": {
    "globalInputs": ["input_index_filter"],
    "structure": [...]
  },
  "dataSources": {
    "ds_events": {
      "options": {
        "query": "index IN (\"security\",\"firewall\",\"ids\",\"endpoint\") | stats count | eval status=case(count>500,\"High\",1=1,\"Normal\")"
      }
    }
  }
}
```

## 🔍 Validation Enhancements

### Standard Validation
- JSON syntax validation
- Template structure validation  
- Parameter type checking
- Handlebars syntax validation

### NEW: Strict Mode (`--strict`)
```bash
uv run create-dashboard validate-template template_name --strict
```

**Additional Checks:**
- **Performance**: Complex query detection, large dashboard size warnings
- **Security**: Wildcard search patterns, unbounded time ranges
- **Best Practices**: Deprecated Splunk syntax detection
- **Splunk Compatibility**: Dashboard Studio structure validation

### Example Strict Mode Output
```
✅ Template validation passed!

⚠️  Warnings:
• Found 3 complex queries - consider simplifying for performance
• Wildcard searches found - ensure appropriate time bounds for security
• Consider using stats instead of join for better performance
```

## 🚀 Migration Path

### Phase 1: Current (Working Now)
- ✅ Both `.json` and `.json.hbs` formats supported
- ✅ Enhanced validation with comprehensive test context
- ✅ Strict validation mode

### Phase 2: Future Enhancements  
- **Schema Validation**: YAML schema files for parameter validation
- **Template Compilation**: Pre-compiled templates for performance
- **Custom Helpers**: User-defined Handlebars helpers
- **Template Inheritance**: Template extends/includes

## 🎯 Best Practices

### 1. **Template Organization**
```
templates/dashboard-templates/
├── basic_monitoring.json          # Simple templates
├── security_advanced.json.hbs     # Complex templates with logic
└── schemas/
    └── security_advanced.yaml     # Future: Parameter schemas
```

### 2. **Parameter Design**
```handlebars
"parameters": {
  "security_indexes": {
    "type": "array",
    "description": "List of security indexes to monitor",
    "default": ["security", "firewall"], 
    "validation": "non-empty",           // Future enhancement
    "required": true
  }
}
```

### 3. **Template Logic**
```handlebars
// ✅ Good: Clear conditional structure
{{#if enable_advanced_features}}
{
  "item": "advanced_viz",
  "options": {...}
}{{/if}}

// ❌ Avoid: Complex nested logic in templates
```

### 4. **Performance Considerations**
```handlebars
// ✅ Good: Efficient queries
"query": "index={{primary_index}} | stats count by sourcetype"

// ⚠️  Consider: Complex queries that may impact performance
"query": "index=* | join src_ip [search index=threats] | transaction user"
```

## 🔧 Troubleshooting

### Common Issues

1. **JSON Syntax Errors**
   ```
   Error: Expecting ',' delimiter
   ```
   **Solution**: Check comma placement around `{{#each}}` blocks

2. **Template Validation Fails**
   ```
   Error: Template rendering produces invalid JSON
   ```
   **Solution**: Use `--strict` mode for detailed error analysis

3. **Missing Parameters**
   ```
   Error: Required parameter 'security_indexes' not provided
   ```
   **Solution**: Add to config file or set defaults in template

### Debug Commands
```bash
# Detailed validation
uv run create-dashboard validate-template template_name --strict

# Test with minimal config
echo '{"dashboard_title": "Test"}' > debug_config.json
uv run create-dashboard generate template_name --config-file debug_config.json --dry-run
```

## 🤝 Contributing Templates

When creating new Handlebars templates:

1. **Use descriptive names**: `security_incident_response.json.hbs`
2. **Add format indicator**: `"format": "handlebars"` in template_info
3. **Test both formats**: Validate with and without `--strict`
4. **Document parameters**: Clear descriptions and sensible defaults
5. **Follow JSON structure**: Valid Dashboard Studio JSON output

The Handlebars template system provides powerful capabilities while maintaining backward compatibility with existing `.json` templates!