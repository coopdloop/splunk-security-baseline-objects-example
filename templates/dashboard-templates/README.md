# Dashboard Templates

This directory contains parameterized JSON dashboard templates for generating customized Splunk dashboards.

## Available Templates

### Data Source Validation (`data_source_validation.json`)
**Purpose**: Monitor data ingestion, validate source availability, and identify missing data
**Use Cases**: 
- Monitoring data pipeline health
- Identifying stale or missing data sources
- Tracking ingestion rates and volumes

### Streams Monitoring (`streams_monitoring.json`)  
**Purpose**: Monitor Splunk Streams performance, capture rates, and network traffic analysis
**Use Cases**:
- Network packet capture monitoring
- Streams performance optimization
- Protocol analysis and traffic patterns

### CIM Compliance (`cim_compliance.json`)
**Purpose**: Validate Common Information Model compliance across data sources and data models
**Use Cases**:
- CIM field population validation
- Data model acceleration monitoring  
- Sourcetype compliance reporting

## Template Structure

Each template contains:
- **template_info**: Metadata about the template
- **parameters**: Configurable parameters with types and defaults
- **dashboard**: Splunk Dashboard Studio JSON definition

### Parameter Types

- **string**: Text input (default values can use `{{ENV_NAME}}` variables)
- **number**: Numeric input (integer or float)
- **boolean**: True/false input
- **array**: Comma-separated list input
- **object**: Complex object (uses defaults, editing not yet implemented)

### Template Variables

Templates support:
- **Variable substitution**: `{{parameter_name}}`
- **Environment variables**: `{{ENV_NAME}}` 
- **Array iteration**: `{{#each array_name}}...{{/each}}`
- **Conditionals**: `{{#if condition}}...{{/if}}`
- **Filters**: `{{value|filter}}` (title, upper, lower, replace)

## Usage

### Interactive Mode
```bash
# Run interactive dashboard generator
./environment-management/scripts/create-dashboard.py

# Specify template and environment
./environment-management/scripts/create-dashboard.py data_source_validation --environment=production
```

### Command Line Mode
```bash
# List available templates
./environment-management/scripts/create-dashboard.py --list

# Generate with specific parameters
./environment-management/scripts/create-dashboard.py cim_compliance \
  --environment=staging \
  --output-dir=environments/staging/dashboards/compliance
```

### Output Structure
Generated dashboards include:
- `{dashboard_name}.json` - Dashboard Studio JSON
- `{dashboard_name}_metadata.json` - Generation metadata and parameters

## Creating New Templates

### 1. Template File Structure
```json
{
  "template_info": {
    "name": "template_name",
    "title": "Human Readable Title", 
    "description": "Template description",
    "category": "validation|monitoring|compliance|analysis",
    "version": "1.0.0"
  },
  "parameters": {
    "parameter_name": {
      "type": "string|number|boolean|array|object",
      "description": "Parameter description",
      "default": "default_value",
      "required": true|false
    }
  },
  "dashboard": {
    // Splunk Dashboard Studio JSON with {{template_variables}}
  }
}
```

### 2. Parameter Best Practices
- Use descriptive parameter names
- Provide sensible defaults
- Use `{{ENV_NAME}}` in defaults for environment-specific values
- Make commonly changed values configurable
- Keep required parameters minimal

### 3. Dashboard JSON Guidelines
- Use Splunk Dashboard Studio format (version 1.1+)
- Parameterize index names, time ranges, and thresholds
- Include proper error handling in searches
- Use consistent visualization types
- Add helpful titles and descriptions

### 4. Testing Templates
```bash
# Test template syntax
python3 -m json.tool template_name.json

# Generate test dashboard
./environment-management/scripts/create-dashboard.py template_name \
  --environment=development \
  --output-dir=test_output
```

## Template Development Examples

### Simple Parameter
```json
"dashboard_title": {
  "type": "string",
  "description": "Dashboard title",
  "default": "{{ENV_NAME}} - My Dashboard",
  "required": true
}
```

### Array Parameter with Iteration
```json
// In parameters:
"indexes": {
  "type": "array", 
  "description": "Indexes to search",
  "default": ["security", "firewall"],
  "required": true
}

// In dashboard JSON:
"query": "index IN ({{#each indexes}}\"{{this}}\"{{#unless @last}},{{/unless}}{{/each}})"
```

### Conditional Content
```json
// In dashboard JSON:
{{#if enable_geo_mapping}}
{
  "type": "splunk.choropleth.svg",
  "title": "Geographic Distribution"
}
{{/if}}
```

## Integration with Environment Management

Templates integrate with the multi-environment structure:
- Use `--environment` flag to set `{{ENV_NAME}}` variable
- Output to environment-specific directories
- Inherit environment-specific defaults
- Support environment overrides in parameters

## Troubleshooting

### Common Issues
1. **Template rendering errors**: Check for unmatched brackets or invalid variable references
2. **Missing parameters**: Ensure all required parameters are provided  
3. **Invalid JSON output**: Validate template syntax and parameter values
4. **Search errors**: Test SPL queries manually before using in templates

### Debugging
- Use `--list` to verify template availability
- Check generated `_metadata.json` for parameter values
- Test dashboard JSON in Splunk Dashboard Studio
- Validate searches in Splunk Search & Reporting

### Getting Help
- Review template examples in this directory
- Check parameter descriptions and defaults
- Test with development environment first
- Report issues in repository discussions