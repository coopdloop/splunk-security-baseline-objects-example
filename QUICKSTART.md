# Quick Start Guide

## Setup with uv

### 1. Install uv (if not already installed)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Setup the project
```bash
# Navigate to the project directory
cd splunk-ta-repo

# Create virtual environment and install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### 3. Activate the environment
```bash
# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

## Using the Dashboard Generator

### Interactive Mode (Recommended for first time)

```bash
# List available templates
create-dashboard list-templates

# Generate dashboard interactively
create-dashboard generate data_source_validation --environment production

# The tool will prompt you for:
# - Dashboard title [Production - Data Source Validation]: 
# - Primary security index [security]: 
# - Additional indexes (comma-separated) [firewall, ids, proxy, endpoint]: 
# - Expected daily ingestion in GB [1.0]: 
# - Missing data threshold in minutes [60]: 
# - Output directory [environments/production/dashboards/generated]:
```

### Command Line Mode

```bash
# Generate with specific parameters using a config file
create-dashboard generate cim_compliance \\
  --environment staging \\
  --config-file my_config.json \\
  --output-dir custom/output/path

# Dry run to see what would be generated
create-dashboard generate streams_monitoring \\
  --environment development \\
  --dry-run
```

### Validate Templates

```bash
# Validate a template structure
create-dashboard validate-template data_source_validation
```

## Real Working Example

Let me walk you through generating a real dashboard:

### Step 1: Check available templates
```bash
create-dashboard list-templates
```

**Output:**
```
📊 Available Dashboard Templates
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                 ┃ Title                         ┃ Category  ┃ Description                                                                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ data_source_validation │ Data Source Validation Dashboard │ validation │ Validates data sources, monitors ingestion rates, and identifies missing data...        │
│ streams_monitoring   │ Splunk Streams Monitoring Dashboard │ monitoring │ Monitor Splunk Streams performance, capture rates, and network traffic analysis...     │
│ cim_compliance       │ CIM Compliance Validation Dashboard │ compliance │ Validate Common Information Model compliance across data sources and data models...    │
└──────────────────────┴───────────────────────────────────┴───────────┴─────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 2: Generate a dashboard interactively
```bash
create-dashboard generate data_source_validation --environment production
```

**Interactive Session:**
```
🎯 Dashboard Template
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Data Source Validation Dashboard                                                                            │
│ Validates data sources, monitors ingestion rates, and identifies missing data                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🔧 Configuration

dashboard_title (string)
Dashboard title
Enter dashboard_title [Production - Data Source Validation]: Production SOC Data Health

dashboard_description (string)
Dashboard description
Enter dashboard_description [Monitor data ingestion and validate source availability]: 

primary_index (string)
Primary security index to monitor
Enter primary_index [security]: 

secondary_indexes (array)
Additional indexes to monitor
Enter secondary_indexes (comma-separated) [firewall, ids, proxy, endpoint]: firewall, ids, wineventlog

expected_sources_lookup (string)
Lookup table containing expected data sources
Enter expected_sources_lookup [expected_data_sources.csv]: 

ingestion_threshold_gb (number)
Minimum expected daily ingestion in GB
Enter ingestion_threshold_gb [1.0]: 5.0

missing_data_threshold_minutes (number)
Alert if no data received in X minutes
Enter missing_data_threshold_minutes [60]: 30

🔨 Generating dashboard...

🎉 Success
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✅ Dashboard generated successfully!                                                                        │
│ 📄 Dashboard: environments/production/dashboards/generated/production_soc_data_health.json                 │
│ 📋 Metadata: environments/production/dashboards/generated/production_soc_data_health_metadata.json         │
│                                                                                                              │
│ Next steps:                                                                                                  │
│ 1. Import JSON into Splunk Dashboard Studio                                                                 │
│ 2. Verify searches execute correctly                                                                        │
│ 3. Customize visualizations as needed                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Step 3: Review generated files

**Generated Dashboard JSON** (`production_soc_data_health.json`):
```json
{
  "version": "1.1",
  "hideTitle": false,
  "title": "Production SOC Data Health",
  "description": "Monitor data ingestion and validate source availability",
  "definition": {
    "type": "absolute_time.earliest_time",
    "value": "-24h@h"
  },
  "inputs": [
    {
      "type": "time",
      "token": "time_picker",
      "title": "Time Range",
      "defaultValue": {
        "earliest_time": "-24h@h",
        "latest_time": "now"
      }
    },
    {
      "type": "dropdown",
      "token": "index_filter",
      "title": "Index Filter",
      "selectFirstChoice": true,
      "choices": [
        {"label": "All Monitored Indexes", "value": "*"},
        {"label": "Security", "value": "security"},
        {"label": "Firewall", "value": "firewall"},
        {"label": "Ids", "value": "ids"},
        {"label": "Wineventlog", "value": "wineventlog"}
      ],
      "defaultValue": "security"
    }
  ],
  "dataSources": {
    "ds_ingestion_summary": {
      "type": "ds.search",
      "options": {
        "query": "index=security OR index IN (\"firewall\",\"ids\",\"wineventlog\") | stats count as total_events, dc(source) as unique_sources, round(sum(eval(len(_raw)))/1024/1024/1024,2) as total_gb by index | eval health_status=case(total_gb>5.0,\"Healthy\",total_gb>2.5,\"Warning\",1=1,\"Critical\")",
        "queryParameters": {
          "earliest": "$time_picker.earliest$",
          "latest": "$time_picker.latest$"
        }
      }
    }
  }
}
```

**Metadata File** (`production_soc_data_health_metadata.json`):
```json
{
  "template_used": "data_source_validation",
  "template_version": "1.0.0",
  "generated_at": "2025-01-09T10:30:15.123456",
  "generated_by": "splunk-ta-repo dashboard generator",
  "parameters": {
    "ENV_NAME": "production",
    "dashboard_title": "Production SOC Data Health",
    "primary_index": "security",
    "secondary_indexes": ["firewall", "ids", "wineventlog"],
    "ingestion_threshold_gb": 5.0,
    "missing_data_threshold_minutes": 30
  },
  "splunk_version": "9.0+",
  "dashboard_type": "splunk_dashboard_studio"
}
```

## Development and Testing

### Run tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/splunk_ta_repo --cov-report=html

# Run specific test
uv run pytest tests/test_dashboard_generator.py::test_generate_dashboard
```

### Code formatting and linting
```bash
# Format code
uv run black src/ tests/

# Lint code  
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Using with config files

Create a config file (`my_dashboard_config.json`):
```json
{
  "dashboard_title": "Security Operations Dashboard",
  "primary_index": "security", 
  "secondary_indexes": ["firewall", "ids", "proxy"],
  "ingestion_threshold_gb": 10.0,
  "missing_data_threshold_minutes": 15
}
```

Then generate:
```bash
create-dashboard generate data_source_validation \\
  --environment production \\
  --config-file my_dashboard_config.json
```

## Integration with Environment Management

The dashboard generator integrates seamlessly with the multi-environment system:

```bash
# Generate for different environments
create-dashboard generate cim_compliance --environment development
create-dashboard generate cim_compliance --environment staging  
create-dashboard generate cim_compliance --environment production

# Each will use environment-specific defaults and output to the correct directory
```

## Next Steps

1. **Import to Splunk**: Copy the generated JSON and import it in Splunk Dashboard Studio
2. **Customize**: Modify visualizations, colors, and layouts as needed
3. **Test**: Verify all searches execute properly with your data
4. **Iterate**: Update templates or create new ones for your specific use cases

The dashboard generator gives you a powerful foundation for creating consistent, parameterized dashboards across all your Splunk environments!