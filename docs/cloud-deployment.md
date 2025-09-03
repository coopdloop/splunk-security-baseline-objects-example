# Splunk Cloud Deployment Guide

This guide covers deploying knowledge objects, data models, and dashboards to Splunk Cloud environments.

## Splunk Cloud Considerations

### Deployment Methods
1. **Splunk Cloud Gateway** - Preferred method for production deployments
2. **Manual Upload** - For development and testing
3. **API-based Deployment** - For automated deployments

### Restrictions and Limitations

#### File System Access
- No direct file system access to Splunk Cloud instances
- All configurations must be deployed through approved methods
- Custom scripts require Splunk approval process

#### Configuration Files
- Limited access to certain configuration files
- Some advanced configurations require Splunk support
- Props.conf and transforms.conf changes require validation

## Deployment Workflows

### Method 1: Splunk Cloud Gateway

#### Prerequisites
- Access to Splunk Cloud Gateway
- Appropriate deployment permissions
- Validated configuration packages

#### Steps
1. **Package Preparation**
```bash
# Create deployment package
mkdir splunk_ta_deployment
cp -r knowledge-objects/ splunk_ta_deployment/
cp -r data-models/ splunk_ta_deployment/
cp -r dashboards/ splunk_ta_deployment/
```

2. **Configuration Validation**
```bash
# Validate syntax
splunk btool check --debug
```

3. **Deploy via Gateway**
- Upload package to Splunk Cloud Gateway
- Review deployment plan
- Execute deployment during maintenance window

### Method 2: Manual Configuration

#### Knowledge Objects Deployment
1. **Field Extractions**
   - Navigate to Settings > Fields > Field extractions
   - Import props.conf configurations manually
   - Test extractions with sample data

2. **Lookups**
   - Upload CSV files via Settings > Lookups > Lookup table files
   - Create lookup definitions via Settings > Lookups > Lookup definitions
   - Configure automatic lookups if needed

3. **Data Models**
   - Access Settings > Data models
   - Import or recreate data model configurations
   - Configure acceleration settings

#### Dashboard Deployment
1. **Import Dashboards**
   - Navigate to Dashboards & Visualizations
   - Create new dashboard from XML
   - Paste dashboard XML content
   - Validate all panels load correctly

2. **Saved Searches**
   - Access Settings > Searches, reports, and alerts
   - Create new saved searches
   - Configure scheduling and alerting

### Method 3: API Deployment

#### REST API Endpoints
```bash
# Deploy saved searches
curl -k -u username:password \
  -d "name=search_name&search=your_search_here" \
  https://your-instance.splunkcloud.com:8089/services/saved/searches

# Deploy lookups
curl -k -u username:password \
  -d "name=lookup_name&filename=lookup.csv" \
  https://your-instance.splunkcloud.com:8089/services/data/lookup-table-files

# Deploy knowledge objects
curl -k -u username:password \
  -d "stanza_name&key=value" \
  https://your-instance.splunkcloud.com:8089/services/properties/props
```

## Cloud-Specific Configurations

### Index Management
```ini
# indexes.conf (requires Splunk support)
[security]
homePath = $SPLUNK_DB/security/db
coldPath = $SPLUNK_DB/security/colddb
thawedPath = $SPLUNK_DB/security/thaweddb
maxDataSize = auto_high_volume
maxHotBuckets = 10
maxWarmDBCount = 300
```

### App Configuration
```ini
# app.conf for cloud deployment
[install]
is_configured = true
state = enabled

[ui]
is_visible = true
label = Security TA Repository

[launcher]
author = Security Team
version = 1.0.0
description = Security Technical Add-on Repository Template
```

### Permissions
```ini
# metadata/default.meta
[views/*]
export = system

[savedsearches/*] 
export = system

[lookups/*]
export = system

[macros/*]
export = system
```

## Performance Optimization for Cloud

### Data Model Acceleration
```ini
# Optimize for cloud storage
[SecurityDataModel]
acceleration = true
acceleration.earliest_time = -30d@d
acceleration.max_concurrent = 1
acceleration.max_time = 7200
acceleration.cron_schedule = 15 1 * * *
```

### Search Optimization
- Use time-based filters aggressively
- Leverage summary indexing for complex calculations
- Implement search head clustering awareness
- Monitor search job inspector for performance

### Resource Management
- Configure appropriate search timeouts
- Limit concurrent search jobs
- Use search scheduling efficiently  
- Monitor cloud compute usage

## Testing and Validation

### Pre-Deployment Testing
1. **Syntax Validation**
```spl
# Test field extractions
| makeresults | eval _raw="sample_log_data" | props your_sourcetype

# Validate lookup functionality  
| inputlookup threat_indicators | head 10

# Test macro expansion
| makeresults | `security_macros` | head 1
```

2. **Performance Testing**
```spl
# Test data model performance
| datamodel Authentication search | head 1000
| eval search_time=now()-info_min_time

# Validate dashboard load times
| rest /services/data/ui/views | search title="*Security*"
```

### Post-Deployment Verification
1. Confirm all knowledge objects deployed successfully
2. Validate data model acceleration
3. Test dashboard functionality
4. Verify saved search execution
5. Check alert triggering

## Troubleshooting Common Issues

### Configuration Conflicts
- Check for duplicate stanza names
- Validate precedence order
- Review app loading sequence
- Examine btool output

### Performance Issues
- Monitor search job performance
- Check data model acceleration status
- Review index configuration
- Analyze search head resource usage

### Permission Problems
- Verify role-based access controls
- Check object sharing settings
- Review capability assignments
- Validate app permissions

## Rollback Procedures

### Emergency Rollback
1. Disable problematic configurations
2. Restore previous working state
3. Document issues encountered
4. Plan remediation steps

### Configuration Backup
```bash
# Export current configurations
splunk export config > backup_$(date +%Y%m%d).xml

# Export specific objects
splunk export savedsearch "search_name"
splunk export dashboard "dashboard_name"
```

## Support and Escalation

### When to Contact Splunk Support
- Index configuration changes
- Advanced authentication configurations
- Performance optimization assistance
- Custom app approval requests

### Documentation Requirements
- Detailed change descriptions
- Business justification
- Performance impact assessment
- Rollback procedures

For additional cloud-specific guidance, consult the [Splunk Cloud Administration Manual](https://docs.splunk.com/Documentation/SplunkCloud).