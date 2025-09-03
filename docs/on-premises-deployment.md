# On-Premises Deployment Guide

This guide covers deploying knowledge objects, data models, and dashboards to on-premises Splunk environments.

## Deployment Architecture

### Typical On-Premises Setup
```
Search Head Cluster
├── Knowledge Objects (props.conf, transforms.conf)
├── Data Models & Acceleration
└── Dashboards & Saved Searches

Indexer Cluster  
├── Index Configurations
└── Data Processing Rules

Deployment Server
├── App Distribution
└── Configuration Management
```

### File Locations
- **Search Heads**: `$SPLUNK_HOME/etc/apps/your_app/`
- **Indexers**: `$SPLUNK_HOME/etc/master-apps/your_app/` 
- **Universal Forwarders**: `$SPLUNK_HOME/etc/apps/your_app/`

## Deployment Methods

### Method 1: Direct File Deployment

#### Single Instance Deployment
```bash
# Create app directory structure
mkdir -p $SPLUNK_HOME/etc/apps/security_ta_repo/{default,metadata,lookups}

# Copy knowledge objects
cp knowledge-objects/field-extractions/* $SPLUNK_HOME/etc/apps/security_ta_repo/default/
cp knowledge-objects/transforms/* $SPLUNK_HOME/etc/apps/security_ta_repo/default/
cp knowledge-objects/lookups/*.csv $SPLUNK_HOME/etc/apps/security_ta_repo/lookups/

# Set permissions
chown -R splunk:splunk $SPLUNK_HOME/etc/apps/security_ta_repo
chmod 644 $SPLUNK_HOME/etc/apps/security_ta_repo/default/*

# Restart Splunk
$SPLUNK_HOME/bin/splunk restart
```

#### Search Head Cluster Deployment
```bash
# Deploy to cluster master
cp -r security_ta_repo/ $SPLUNK_HOME/etc/shcluster/apps/

# Apply cluster bundle
splunk apply shcluster-bundle -target https://sh1.example.com:8089 -auth admin:password

# Verify deployment
splunk show shcluster-status
```

### Method 2: Deployment Server

#### Configure Deployment Server
```ini
# serverclass.conf
[serverClass:security_apps]
whitelist.0 = search_head_*
whitelist.1 = indexer_*

[serverClass:security_apps:app:security_ta_repo]
restartSplunkd = true
restartSplunkWeb = false
stateOnClient = enabled
```

#### Deploy App Package
```bash
# Create deployment package
mkdir -p $SPLUNK_HOME/etc/deployment-apps/security_ta_repo

# Copy app contents
cp -r data-models/ $SPLUNK_HOME/etc/deployment-apps/security_ta_repo/
cp -r knowledge-objects/ $SPLUNK_HOME/etc/deployment-apps/security_ta_repo/
cp -r dashboards/ $SPLUNK_HOME/etc/deployment-apps/security_ta_repo/

# Reload deployment server
splunk reload deploy-server
```

### Method 3: Indexer Cluster Manager

#### For Knowledge Objects on Indexers
```bash
# Deploy to cluster master
cp -r security_ta_repo/ $SPLUNK_HOME/etc/master-apps/

# Apply cluster bundle
splunk apply cluster-bundle

# Verify bundle deployment
splunk show cluster-bundle-status
```

## Configuration Management

### App Structure
```
security_ta_repo/
├── default/
│   ├── app.conf
│   ├── props.conf
│   ├── transforms.conf
│   ├── macros.conf
│   ├── eventtypes.conf
│   ├── tags.conf
│   ├── datamodels.conf
│   └── savedsearches.conf
├── metadata/
│   └── default.meta
├── lookups/
│   ├── threat_indicators.csv
│   ├── asset_inventory.csv
│   └── geoip_database.csv
└── local/
    └── (user customizations)
```

### Required Configuration Files

#### app.conf
```ini
[install]
is_configured = true
state = enabled

[ui]
is_visible = true
label = Security TA Repository

[launcher]
author = Security Engineering Team
version = 1.0.0
description = Technical Add-on repository for security monitoring and analysis

[package]
id = security_ta_repo
check_for_updates = false
```

#### metadata/default.meta
```ini
# Global permissions
[]
access = read : [ * ], write : [ admin, sc_admin ]
export = system

[views/*]
export = system

[savedsearches/*]
export = system

[macros/*] 
export = system

[lookups/*]
export = system

[eventtypes/*]
export = system

[tags/*]
export = system
```

## Index Configuration

### Security Indexes
```ini
# indexes.conf
[security]
homePath = $SPLUNK_DB/security/db
coldPath = $SPLUNK_DB/security/colddb  
thawedPath = $SPLUNK_DB/security/thaweddb
maxDataSize = auto_high_volume
maxHotBuckets = 10
maxWarmDBCount = 300
repFactor = auto

[firewall]
homePath = $SPLUNK_DB/firewall/db
coldPath = $SPLUNK_DB/firewall/colddb
thawedPath = $SPLUNK_DB/firewall/thaweddb
maxDataSize = auto
repFactor = auto

[ids] 
homePath = $SPLUNK_DB/ids/db
coldPath = $SPLUNK_DB/ids/colddb
thawedPath = $SPLUNK_DB/ids/thaweddb
maxDataSize = auto
repFactor = auto
```

### Data Retention Policies
```ini
# Configure retention based on data criticality
[security]
maxDataSize = 100GB
frozenTimePeriodInSecs = 7776000  # 90 days

[firewall]
maxDataSize = 500GB 
frozenTimePeriodInSecs = 15552000 # 180 days

[audit]
maxDataSize = 50GB
frozenTimePeriodInSecs = 31536000 # 1 year
```

## Performance Tuning

### Search Head Optimization
```ini
# limits.conf
[search]
max_searches_per_cpu = 1
max_rt_search_multiplier = 1
max_searchinfo_map_entries = 1000

# Data model acceleration
[datamodel_acceleration]
max_concurrent = 3
max_time = 3600
```

### Indexer Optimization
```ini
# server.conf
[general]
parallelIngestionPipelines = 2

[kvstore]
disabled = false
storageEngine = mmapv1

[clustering]
mode = slave
master_uri = https://cluster-master:8089
```

## Monitoring and Maintenance

### Health Checks
```spl
# Monitor data model acceleration
| rest /services/data/models
| search acceleration=1
| eval last_updated=strftime(acceleration.earliest_time,"%Y-%m-%d %H:%M:%S")
| table title, acceleration.earliest_time, acceleration.summary_size

# Check knowledge object deployment
| rest /services/configs/conf-props
| search title="*security*"
| stats count by eai:appName

# Verify lookup table updates
| rest /services/data/lookup-table-files  
| eval file_size_mb=round(eai:data/1024/1024,2)
| table title, eai:userName, updated, file_size_mb
```

### Performance Monitoring
```spl
# Monitor search performance  
index=_audit action=search
| eval search_duration=total_run_time
| stats avg(search_duration), max(search_duration), count by app
| sort -avg(search_duration)

# Data model acceleration monitoring
index=_internal source=*splunkd.log component=DataModelAccelerationManager
| stats count by log_level, message
```

### Maintenance Tasks

#### Regular Maintenance (Weekly)
- Review data model acceleration status
- Update threat intelligence lookups
- Validate dashboard performance
- Check for configuration drift

#### Monthly Maintenance
- Analyze storage usage and retention
- Review and update asset inventory
- Performance tuning analysis
- Security configuration audit

#### Quarterly Maintenance
- Major lookup table updates
- Data model optimization
- Dashboard refresh and updates
- Knowledge object cleanup

## Backup and Recovery

### Configuration Backup
```bash
# Backup entire app
tar -czf security_ta_backup_$(date +%Y%m%d).tar.gz $SPLUNK_HOME/etc/apps/security_ta_repo/

# Backup specific configurations
cp $SPLUNK_HOME/etc/apps/security_ta_repo/default/*.conf ./config_backup/
cp $SPLUNK_HOME/etc/apps/security_ta_repo/lookups/*.csv ./lookup_backup/
```

### Restoration Process
```bash
# Stop Splunk services
$SPLUNK_HOME/bin/splunk stop

# Restore configurations
tar -xzf security_ta_backup_20240101.tar.gz -C $SPLUNK_HOME/etc/apps/

# Set permissions
chown -R splunk:splunk $SPLUNK_HOME/etc/apps/security_ta_repo

# Start Splunk services
$SPLUNK_HOME/bin/splunk start
```

## Security Best Practices

### Access Control
- Implement role-based access control (RBAC)
- Use principle of least privilege
- Regular access review and cleanup
- Enable audit logging for all changes

### Configuration Security
```ini
# Secure sensitive lookups
[threat_indicators]
access = read : [ security_analyst ], write : [ security_admin ]
export = system
```

### Network Security
- Enable SSL for all Splunk communications
- Configure firewall rules for Splunk ports
- Use certificate-based authentication
- Implement network segmentation

## Troubleshooting

### Common Issues

#### Knowledge Object Not Working
1. Check btool output: `splunk btool props list --debug`
2. Verify app is enabled: `splunk display app security_ta_repo`
3. Review splunkd.log for errors: `index=_internal source=*splunkd.log ERROR`

#### Data Model Acceleration Issues  
1. Check acceleration status: `| datamodel YourModel search | head 1`
2. Review acceleration logs: `index=_internal source=*splunkd.log component=DataModelAccelerationManager`
3. Rebuild acceleration: Settings > Data models > Rebuild

#### Dashboard Loading Problems
1. Test individual searches manually
2. Check for missing lookup files
3. Validate macro definitions
4. Review browser console for JavaScript errors

### Log Analysis
```spl
# Check for configuration errors
index=_internal source=*splunkd.log ERROR app=security_ta_repo

# Monitor reload activities
index=_internal source=*splunkd.log "Configuration reloaded"

# Performance monitoring
index=_introspection component=Pipelines
| stats avg(cpu_seconds) by processor
```

## Best Practices Summary

1. **Always test in development first**
2. **Use deployment server for consistency**
3. **Monitor performance impact**
4. **Maintain configuration version control**
5. **Document all customizations**
6. **Regular backup of configurations**
7. **Follow change management procedures**
8. **Keep lookup tables updated**

For specific deployment scenarios, consult your Splunk administrator or the official Splunk Enterprise documentation.