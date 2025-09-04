# Working Example - Dashboard Generation

## Complete Working Example

Here's a step-by-step example of the dashboard generation system in action.

### 1. Setup
```bash
# Setup the project (one-time)
cd splunk-ta-repo
uv sync
```

### 2. List Available Templates
```bash
uv run create-dashboard list-templates
```

**Output:**
```
📊 Available Dashboard Templates                        
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                ┃ Title               ┃ Category   ┃ Description         ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ simple_data_valida… │ Simple Data         │ validation │ Basic data source   │
│                     │ Validation          │            │ validation and      │
│                     │ Dashboard           │            │ monitoring...       │
└─────────────────────┴─────────────────────┴────────────┴─────────────────────┘
```

### 3. Create Configuration File
Create a file `production_config.json`:
```json
{
  "dashboard_title": "Production Data Health Monitor",
  "primary_index": "security", 
  "time_range_earliest": "-4h@h"
}
```

### 4. Generate Dashboard
```bash
uv run create-dashboard generate simple_data_validation \\
  --environment production \\
  --config-file production_config.json \\
  --output-dir environments/production/dashboards/generated
```

**Output:**
```
╭─────────────────────────── 🎯 Dashboard Template ────────────────────────────╮
│ Simple Data Validation Dashboard                                             │
│ Basic data source validation and monitoring                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Loaded parameters from production_config.json
🔨 Generating dashboard...
╭───────────────────────────────── 🎉 Success ─────────────────────────────────╮
│ ✅ Dashboard generated successfully!                                         │
│ 📄 Dashboard:                                                                │
│ environments/production/dashboards/generated/production_data_health_monitor. │
│ json                                                                         │
│ 📋 Metadata:                                                                 │  
│ environments/production/dashboards/generated/production_data_health_monitor_ │
│ metadata.json                                                                │
│                                                                              │
│ Next steps:                                                                  │
│ 1. Import JSON into Splunk Dashboard Studio                                  │
│ 2. Verify searches execute correctly                                         │
│ 3. Customize visualizations as needed                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 5. Generated Dashboard JSON
The generated `production_data_health_monitor.json` contains:

```json
{
  "version": "1.1",
  "hideTitle": false,
  "title": "Production Data Health Monitor",
  "description": "Monitor data ingestion and validate source availability",
  "definition": {
    "type": "absolute_time.earliest_time",
    "value": "-4h@h"
  },
  "inputs": [
    {
      "type": "time",
      "token": "time_picker", 
      "title": "Time Range",
      "defaultValue": {
        "earliest_time": "-4h@h",
        "latest_time": "now"
      }
    }
  ],
  "dataSources": {
    "ds_events": {
      "type": "ds.search",
      "options": {
        "query": "index=security | stats count as total_events",
        "queryParameters": {
          "earliest": "$time_picker.earliest$",
          "latest": "$time_picker.latest$"
        }
      }
    },
    "ds_sources": {
      "type": "ds.search",
      "options": {
        "query": "index=security | stats dc(source) as unique_sources", 
        "queryParameters": {
          "earliest": "$time_picker.earliest$",
          "latest": "$time_picker.latest$"
        }
      }
    }
  },
  "visualizations": {
    "viz_event_count": {
      "type": "splunk.singlevalue",
      "title": "Total Events",
      "options": {
        "majorValue": "> primary | seriesByName('total_events')",
        "numberPrecision": 0
      }
    },
    "viz_source_count": {
      "type": "splunk.singlevalue", 
      "title": "Unique Sources",
      "options": {
        "majorValue": "> primary | seriesByName('unique_sources')",
        "numberPrecision": 0
      }
    }
  }
}
```

### 6. Generated Metadata
The `production_data_health_monitor_metadata.json` tracks:

```json
{
  "template_used": "simple_data_validation",
  "template_version": "1.0.0",
  "generated_at": "2025-09-04T14:10:37.021170",
  "generated_by": "splunk-ta-repo dashboard generator",
  "parameters": {
    "dashboard_title": "Production Data Health Monitor",
    "primary_index": "security",
    "time_range_earliest": "-4h@h"
  },
  "splunk_version": "9.0+",
  "dashboard_type": "splunk_dashboard_studio"
}
```

### 7. Validate Templates
```bash
uv run create-dashboard validate-template simple_data_validation
```

**Output:**
```
╭───────────────────────────── Validation Results ─────────────────────────────╮
│ ✅ Template validation passed!                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 8. Import to Splunk

1. **Open Splunk Dashboard Studio**
2. **Create New Dashboard > Start from scratch**  
3. **Switch to Source mode (</> icon)**
4. **Paste the generated JSON**
5. **Save the dashboard**

The dashboard will show:
- **Total Events** - Single value showing event count from security index
- **Unique Sources** - Single value showing number of data sources
- **Time picker** - Interactive time range selection

### 9. Test Different Environments

```bash
# Development environment
uv run create-dashboard generate simple_data_validation \\
  --environment development \\
  --config-file dev_config.json

# Staging environment  
uv run create-dashboard generate simple_data_validation \\
  --environment staging \\
  --config-file staging_config.json
```

Each environment can have different:
- Index names (`primary_index`)
- Time ranges (`time_range_earliest`)
- Dashboard titles
- Output directories

## Key Benefits Demonstrated

✅ **Parameterized Templates** - Same template, different configurations  
✅ **Environment-Specific** - Automatic environment context (`production`, `staging`, etc.)  
✅ **Version Tracking** - Metadata files track what was generated and when  
✅ **Validation** - Template structure and syntax validation  
✅ **CLI Integration** - Beautiful, rich terminal interface  
✅ **Configuration Files** - Reusable parameter configurations  
✅ **Ready for Splunk** - Generated JSON imports directly into Dashboard Studio

## Next Steps

1. **Create more templates** for your specific monitoring needs
2. **Integrate with CI/CD** for automated dashboard deployment
3. **Add custom parameters** for your environment-specific requirements
4. **Build template library** for your team's common dashboard patterns

The system provides a solid foundation for scaling dashboard creation across multiple Splunk environments while maintaining consistency and tracking changes.