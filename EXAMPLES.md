# 🚀 Examples & Use Cases

## Complete Feature Demonstration

### 1. **List All Templates (Both Formats)**
```bash
$ uv run create-dashboard list-templates
                        📊 Available Dashboard Templates                        
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                ┃ Title               ┃ Category   ┃ Description         ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ cim_compliance      │ CIM Compliance      │ compliance │ Validate Common     │
│                     │ Validation          │            │ Information Model   │
│                     │ Dashboard           │            │ compliance acros... │
│ simple_data_valida… │ Simple Data         │ validation │ Basic data source   │
│                     │ Validation          │            │ validation and      │
│                     │ Dashboard           │            │ monitoring...       │
│ data_source_valida… │ Data Source         │ validation │ Validates data      │
│                     │ Validation          │            │ sources, monitors   │
│                     │ Dashboard           │            │ ingestion rates,    │
│                     │                     │            │ ...                 │
│ streams_monitoring  │ Splunk Streams      │ monitoring │ Monitor Splunk      │
│                     │ Monitoring          │            │ Streams             │
│                     │ Dashboard           │            │ performance,        │
│                     │                     │            │ capture rates,...   │
│ security_basic      │ Basic Security      │ security   │ Simple security     │ ← NEW!
│                     │ Dashboard           │            │ monitoring          │
│                     │                     │            │ dashboard with      │
│                     │                     │            │ event tr...         │
└─────────────────────┴─────────────────────┴────────────┴─────────────────────┘
```

### 2. **Enhanced Validation (Basic)**
```bash
$ uv run create-dashboard validate-template security_basic
╭───────────────────────────── Validation Results ─────────────────────────────╮
│ ✅ Template validation passed!                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 3. **🆕 Enhanced Validation (Strict Mode)**
```bash
$ uv run create-dashboard validate-template data_source_validation --strict
╭───────────────────────────── Validation Results ─────────────────────────────╮
│ ✅ Template validation passed!                                               │
│                                                                              │
│ ⚠️  Performance Warnings:                                                   │
│ • Found 2 complex queries - consider simplifying for performance            │
│ • Large dashboard size (95KB) - may impact Splunk performance               │
│                                                                              │
│ 💡 Best Practice Suggestions:                                               │
│ • Consider using stats instead of transaction for better performance        │
│ • Wildcard searches found - ensure appropriate time bounds for security     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 4. **Generate Traditional JSON Template**
```bash
$ uv run create-dashboard generate simple_data_validation \
  --environment production \
  --config-file example_config.json \
  --output-dir test_output

╭─────────────────────────── 🎯 Dashboard Template ────────────────────────────╮
│ Simple Data Validation Dashboard                                             │
│ Basic data source validation and monitoring                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Loaded parameters from example_config.json
🔨 Generating dashboard...
╭───────────────────────────────── 🎉 Success ─────────────────────────────────╮
│ ✅ Dashboard generated successfully!                                         │
│ 📄 Dashboard: test_output/production_data_health_monitor.json                │
│ 📋 Metadata: test_output/production_data_health_monitor_metadata.json        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 5. **🆕 Generate Advanced Handlebars Template**
```bash
# Create config for Handlebars template
$ cat > security_config.json << EOF
{
  "dashboard_title": "Production Security Operations",
  "security_indexes": ["security", "firewall", "ids", "endpoint"],
  "time_range_earliest": "-6h@h", 
  "alert_threshold": 500
}
EOF

$ uv run create-dashboard generate security_basic \
  --environment production \
  --config-file security_config.json \
  --output-dir test_output

╭─────────────────────────── 🎯 Dashboard Template ────────────────────────────╮
│ Basic Security Dashboard                                                     │
│ Simple security monitoring dashboard with event tracking                     │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Loaded parameters from security_config.json
🔨 Generating dashboard...
╭───────────────────────────────── 🎉 Success ─────────────────────────────────╮
│ ✅ Dashboard generated successfully!                                         │
│ 📄 Dashboard: test_output/production_security_operations.json                │
│ 📋 Metadata: test_output/production_security_operations_metadata.json        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 6. **Verify Generated Dashboard Content**
```bash
$ head -20 test_output/production_security_operations.json
{
  "version": "1.1",
  "hideTitle": false,
  "title": "Production Security Operations",  ← Rendered from config
  "description": "Basic security operations monitoring",
  "definition": {
    "type": "absolute_time.earliest_time",
    "value": "-6h@h"  ← From config (not default -24h@h)
  },
  "inputs": [
    {
      "type": "dropdown",
      "choices": [
        {"label": "All Security Indexes", "value": "*"},
        {"label": "Security", "value": "security"},      ← Rendered from array
        {"label": "Firewall", "value": "firewall"},     ← Rendered from array  
        {"label": "Ids", "value": "ids"},               ← Rendered from array
        {"label": "Endpoint", "value": "endpoint"}      ← Rendered from array
      ]
    }
  ]
```

### 7. **Check Metadata Tracking**
```bash
$ cat test_output/production_security_operations_metadata.json
{
  "template_used": "security_basic",
  "template_version": "1.0.0",
  "generated_at": "2025-09-04T14:52:06.320191",
  "generated_by": "splunk-ta-repo dashboard generator",
  "parameters": {
    "dashboard_title": "Production Security Operations",
    "security_indexes": ["security", "firewall", "ids", "endpoint"],
    "time_range_earliest": "-6h@h",
    "alert_threshold": 500
  },
  "splunk_version": "9.0+",
  "dashboard_type": "splunk_dashboard_studio"
}
```

## Template Comparison Examples

### Basic JSON Template (`.json`)
```json
{
  "template_info": {
    "name": "simple_validation"
  },
  "parameters": {
    "primary_index": {"default": "security"}
  },
  "dashboard": {
    "title": "{{dashboard_title}}",
    "dataSources": {
      "ds1": {
        "query": "index={{primary_index}} | stats count"
      }
    }
  }
}
```

### Advanced Handlebars Template (`.json.hbs`)
```handlebars
{
  "template_info": {
    "name": "security_basic",
    "format": "handlebars"
  },
  "parameters": {
    "security_indexes": {"default": ["security", "firewall"]}
  },
  "dashboard": {
    "title": "{{ENV_NAME|title}} Security Dashboard",
    "inputs": [
      {
        "choices": [
          {"label": "All", "value": "*"}{{#each security_indexes}},
          {"label": "{{this|title}}", "value": "{{this}}"}{{/each}}
        ]
      }
    ],
    "dataSources": {
      "ds1": {
        "query": "index IN ({{#each security_indexes}}\"{{this}}\"{{#unless @last}},{{/unless}}{{/each}}) | stats count"
      }
    }
  }
}
```

## Use Case Examples

### 1. **Multi-Environment Security Monitoring**
```bash
# Development environment
cat > dev_security_config.json << EOF
{
  "dashboard_title": "Dev Security Dashboard",
  "security_indexes": ["security", "test_firewall"],
  "alert_threshold": 50
}
EOF

# Production environment
cat > prod_security_config.json << EOF
{
  "dashboard_title": "Production Security Operations Center", 
  "security_indexes": ["security", "firewall", "ids", "endpoint", "proxy"],
  "alert_threshold": 1000
}
EOF

# Generate both
uv run create-dashboard generate security_basic --environment development --config-file dev_security_config.json
uv run create-dashboard generate security_basic --environment production --config-file prod_security_config.json
```

### 2. **Template Validation Pipeline**
```bash
#!/bin/bash
# validate_all_templates.sh

echo "🔍 Validating all templates..."

for template in $(uv run create-dashboard list-templates --format json | jq -r '.templates[].name'); do
  echo "Validating $template..."
  
  if uv run create-dashboard validate-template "$template" --strict; then
    echo "✅ $template passed"
  else
    echo "❌ $template failed"
    exit 1
  fi
done

echo "🎉 All templates validated successfully!"
```

### 3. **CI/CD Integration**
```yaml
# .github/workflows/validate-templates.yml
name: Validate Dashboard Templates
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv sync
      - name: Validate all templates
        run: |
          for template in $(uv run create-dashboard list-templates --format json | jq -r '.templates[].name'); do
            uv run create-dashboard validate-template "$template" --strict
          done
      - name: Generate test dashboards
        run: |
          uv run create-dashboard generate security_basic --environment test --config-file test_config.json
          # Verify generated JSON is valid
          jq . test_output/*.json > /dev/null
```

## Migration Example

### Before (Limited templating)
```json
{
  "dashboard": {
    "title": "{{dashboard_title}}",
    "dataSources": {
      "ds1": {"query": "index=security | stats count"}
    }
  }
}
```

### After (Full Handlebars power)
```handlebars
{
  "dashboard": {
    "title": "{{ENV_NAME|title}} - {{dashboard_title}}",
    "inputs": [
      {{#each security_indexes}}{
        "label": "{{this|title}} Index",
        "token": "{{this}}_filter"
      }{{#unless @last}},{{/unless}}
      {{/each}}
    ],
    "dataSources": {
      {{#each security_indexes}}"ds_{{@index}}": {
        "query": "index={{this}} | stats count as {{this}}_events"
      }{{#unless @last}},{{/unless}}
      {{/each}}
    }
  }
}
```

## Key Benefits Demonstrated

✅ **Backward Compatibility** - All existing `.json` templates continue working  
✅ **Advanced Templating** - Handlebars provides loops, conditionals, filters  
✅ **Enhanced Validation** - Strict mode catches performance and security issues  
✅ **Better Error Messages** - Comprehensive validation with helpful suggestions  
✅ **Template Discovery** - Automatic detection of both `.json` and `.json.hbs` files  
✅ **Metadata Tracking** - Complete auditability of generated dashboards  

The system now provides enterprise-grade template capabilities while maintaining the simplicity of the original approach!