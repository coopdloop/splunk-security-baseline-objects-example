# Data Source Validation Dashboard Examples

This directory contains example configuration files for generating data source validation dashboards for common security technologies.

## 🚀 Quick Start

### Basic Usage
```bash
# Generate dashboard using an example configuration
uv run create-dashboard generate data_source_validation \
  --environment production \
  --config-file data_source_validation_example.json
```

### List All Templates
```bash
uv run create-dashboard list-templates
```

## 📋 Available Example Configurations

### 1. **Cisco ISE** (`data_source_validation_example.json`)
- **Use Case**: Identity Services Engine authentication monitoring
- **Indexes**: security, network, main
- **Sourcetypes**: cisco:ise:syslog, cisco:ise:admin, cisco:ise:accounting
- **CIM Tags**: authentication, network

### 2. **Palo Alto Networks** (`palo_alto_example.json`)  
- **Use Case**: Firewall security monitoring
- **Indexes**: firewall, security, network
- **Sourcetypes**: pan:threat, pan:traffic, pan:system, pan:config
- **CIM Tags**: malware, ids

## 🔧 Creating Custom Configurations

### Required Parameters
```json
{
  "dashboard_title": "Your Dashboard Title",
  "technology_name": "Full Technology Name",
  "technology_short_name": "SHORT", 
  "ta_name": "Splunk_TA_your_app",
  "primary_indexes": ["index1", "index2"],
  "sourcetypes": ["sourcetype:one", "sourcetype:two"],
  "cim_tag_1": "authentication",
  "cim_tag_2": "change", 
  "cim_check_timerange": "-60m@m",
  "global_time_default": "-24h@h,now"
}
```

### Parameter Descriptions
- **dashboard_title**: Display name for your dashboard
- **technology_name**: Full product/technology name (e.g., "Cisco Identity Services Engine")
- **technology_short_name**: Abbreviated name for titles (e.g., "ISE") 
- **ta_name**: Splunk Technical Add-on app name
- **primary_indexes**: Array of Splunk indexes to monitor
- **sourcetypes**: Array of sourcetypes to validate
- **cim_tag_1/cim_tag_2**: CIM data model tags to validate compliance
- **cim_check_timerange**: Time window for CIM compliance checks
- **global_time_default**: Default time range for dashboard

## 📊 Generated Dashboard Features

The data_source_validation template creates dashboards with:

- **📈 Event Volume Monitoring**: Track data ingestion rates
- **🎯 CIM Compliance Validation**: Monitor Common Information Model field population
- **📍 Source Analysis**: Identify data sources and sourcetypes
- **🏠 Host Tracking**: Monitor reporting hosts
- **⚠️ Coverage Metrics**: Calculate percentage CIM compliance
- **📋 Unsupported Events**: Identify events without CIM tags

## 🎨 Customization Examples

### Enterprise Security Focus
```json
{
  "cim_tag_1": "authentication", 
  "cim_tag_2": "malware",
  "primary_indexes": ["notable", "security", "threat_intel"]
}
```

### Network Operations Focus  
```json
{
  "cim_tag_1": "network",
  "cim_tag_2": "ids", 
  "primary_indexes": ["firewall", "ids", "network"]
}
```

### Compliance Monitoring Focus
```json
{
  "cim_tag_1": "change",
  "cim_tag_2": "authentication",
  "primary_indexes": ["audit", "security", "compliance"]
}
```

## 🔍 Testing Your Configuration

1. **Validate Template**:
   ```bash
   uv run create-dashboard validate-template data_source_validation
   ```

2. **Generate Test Dashboard**:
   ```bash
   uv run create-dashboard generate data_source_validation \
     --environment development \
     --config-file your_config.json \
     --output-dir ./test_dashboards
   ```

3. **Import to Splunk**: 
   - Copy the generated JSON file
   - Open Splunk Dashboard Studio
   - Import → JSON → Paste content

## 💡 Pro Tips

- **CIM Tag Selection**: Choose tags that match your data model usage (authentication, malware, network, etc.)
- **Index Strategy**: Include both specific and broad indexes (security, main) for comprehensive monitoring  
- **Sourcetype Precision**: Use exact sourcetype names from your Splunk environment
- **Time Ranges**: Adjust `cim_check_timerange` based on data volume (higher volume = shorter window)

## 🚨 Common Issues & Solutions

### Issue: "No data found"
- **Solution**: Verify index names and sourcetypes match your Splunk environment
- **Check**: Run basic searches like `index=security | head 10` to confirm data exists

### Issue: "CIM tags not found"  
- **Solution**: Ensure CIM compliance is configured for your data sources
- **Check**: Verify tag assignment: `index=security tag=authentication | head 10`

### Issue: "TA not found" error
- **Solution**: Update `ta_name` parameter to match installed app name
- **Check**: Navigate to Apps → Manage Apps in Splunk to find exact name

---

**Need Help?** Check the main repository [README.md](README.md) for additional documentation and examples.