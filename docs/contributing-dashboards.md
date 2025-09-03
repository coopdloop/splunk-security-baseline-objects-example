# Contributing Dashboards

This guide covers creating and contributing security dashboards and saved searches for threat hunting, incident response, and compliance monitoring.

## Overview

Security dashboards provide real-time visibility into threats, incidents, and compliance status. This repository includes templates for common security monitoring use cases.

## Structure

```
dashboards/
├── threat-hunting/      # Proactive threat hunting dashboards
├── incident-response/   # Incident investigation and response
├── compliance/         # Regulatory compliance reporting
└── overview/           # Executive and high-level summaries
```

## Dashboard Types

### 1. Threat Hunting Dashboards
Focus on proactive security monitoring and anomaly detection.

**Categories:**
- Network anomaly detection
- User behavior analytics
- Threat intelligence correlation
- IOC hunting and tracking

### 2. Incident Response Dashboards
Support security incident investigation and response workflows.

**Categories:**
- Timeline reconstruction
- Lateral movement tracking
- Affected asset identification
- Evidence collection

### 3. Compliance Dashboards
Monitor compliance with security frameworks and regulations.

**Categories:**
- NIST Cybersecurity Framework
- PCI DSS monitoring
- GDPR privacy compliance
- SOX audit trails

### 4. Overview Dashboards
Executive and summary views for security leadership.

**Categories:**
- Security metrics overview
- Threat landscape summary
- Incident trends
- Operational metrics

## Contributing Guidelines

### File Naming Convention

#### Dashboard XML Files
`<category>_<specific-use-case>_dashboard.xml`

Examples:
- `threat_hunting_network_anomalies_dashboard.xml`
- `incident_response_timeline_reconstruction_dashboard.xml`
- `compliance_pci_monitoring_dashboard.xml`

#### Saved Searches
`<category>_<specific-use-case>_searches.conf`

Examples:
- `threat_hunting_suspicious_logins_searches.conf`
- `incident_response_lateral_movement_searches.conf`

### Dashboard Structure Template

```xml
<dashboard version="1.1" theme="light">
  <label>Dashboard Title</label>
  <description>Brief description of dashboard purpose</description>
  
  <!-- Input filters -->
  <fieldset submitButton="true" autoRun="false">
    <input type="time" token="time_picker">
      <label>Time Range</label>
      <default>
        <earliest>-24h@h</earliest>
        <latest>now</latest>
      </default>
    </input>
    <input type="dropdown" token="index_filter">
      <label>Data Source</label>
      <choice value="*">All Indexes</choice>
      <choice value="security">Security</choice>
      <default>*</default>
    </input>
  </fieldset>
  
  <row>
    <panel>
      <title>Panel Title</title>
      <single>
        <search>
          <query>
            | datamodel Authentication search 
            | stats count
          </query>
          <earliest>$time_picker.earliest$</earliest>
          <latest>$time_picker.latest$</latest>
        </search>
        <option name="drilldown">none</option>
      </single>
    </panel>
  </row>
</dashboard>
```

### Saved Search Template

```ini
[Security Alert - Suspicious Login Activity]
search = | datamodel Authentication search \
| search action=failure \
| stats count by user, src_ip \
| where count > 10 \
| eval risk_score=case(count>50,"high",count>20,"medium",1=1,"low")

description = Detects users with excessive failed login attempts
dispatch.earliest_time = -1h
dispatch.latest_time = now
cron_schedule = */15 * * * *
enableSched = 1
alert.track = 1
alert.suppress = 0
counttype = number of events
quantity = 1
relation = greater than

action.email = 1
action.email.to = security-team@company.com
action.email.subject = Suspicious Login Activity Detected
```

## Dashboard Categories and Examples

### Threat Hunting

#### Network Anomaly Detection
- DNS tunneling detection
- Unusual network connections
- Data exfiltration patterns
- Command and control communication

**Key Visualizations:**
- Timeline charts for traffic patterns
- Geographic maps for connection sources
- Statistical analysis for baseline deviations
- Network topology diagrams

#### User Behavior Analytics
- Abnormal login patterns
- Privileged account monitoring
- After-hours activity detection
- Access pattern analysis

### Incident Response

#### Timeline Reconstruction
- Event correlation across data sources
- Attack progression tracking
- Asset impact assessment
- Evidence timeline

**Key Components:**
- Interactive timeline visualizations
- Event correlation tables
- Asset relationship mappings
- Evidence collection workflows

### Compliance Monitoring

#### Access Control Monitoring
- User access reviews
- Privileged account auditing
- Permission change tracking
- Segregation of duties validation

#### Data Protection
- Data access monitoring
- Encryption status tracking
- Data loss prevention alerts
- Privacy regulation compliance

## SPL Query Examples

### Basic Threat Hunting
```spl
# Detect rare processes
index=security sourcetype=sysmon EventCode=1
| stats count by Image, CommandLine
| where count < 5
| sort count

# Identify suspicious network connections
| datamodel Network_Traffic search
| search dest_port IN (4444, 5555, 6666, 7777, 8888, 9999)
| stats count by src_ip, dest_ip, dest_port
| sort -count
```

### Incident Response
```spl
# Timeline reconstruction for specific user
index=* user="compromised_user"
| eval event_category=case(
    match(sourcetype,"auth"),"Authentication",
    match(sourcetype,"web"),"Web Activity", 
    match(sourcetype,"network"),"Network",
    1=1,"Other"
)
| table _time, event_category, src_ip, action, details
| sort _time
```

### Compliance Reporting
```spl
# PCI DSS - Credit card data access
index=web sourcetype=access_*
| rex field=uri_query "(?<cc_pattern>\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})"
| where isnotnull(cc_pattern)
| stats count by src_ip, uri_path, user
```

## Performance Best Practices

### Search Optimization
- Use specific time ranges
- Filter by index and sourcetype early
- Leverage data models when possible
- Use statistical commands efficiently
- Implement search acceleration where beneficial

### Dashboard Performance
- Limit concurrent searches
- Use appropriate refresh intervals
- Implement progressive disclosure
- Cache frequently accessed data
- Monitor dashboard load times

## Validation Process

### Testing Checklist
- [ ] Dashboard loads without errors
- [ ] All panels display data correctly
- [ ] Time pickers function properly
- [ ] Drill-down actions work
- [ ] Performance is acceptable
- [ ] Mobile responsiveness verified

### Security Review
- [ ] No sensitive data exposed
- [ ] Appropriate access controls
- [ ] Query performance reviewed
- [ ] Resource usage monitored

## Submission Requirements

### Documentation
Each dashboard contribution must include:

1. **README.md** with:
   - Purpose and use case
   - Required data sources
   - Installation instructions
   - Sample queries

2. **queries.txt** with:
   - All SPL queries used
   - Query explanations
   - Performance notes

3. **screenshots/** folder with:
   - Dashboard screenshots
   - Key visualization examples

### File Structure Example
```
dashboards/threat-hunting/network-anomalies/
├── README.md
├── network_anomalies_dashboard.xml
├── network_anomalies_searches.conf
├── queries.txt
└── screenshots/
    ├── dashboard_overview.png
    └── anomaly_detection_panel.png
```

## Need Help?

- Review existing dashboard examples
- Check Splunk dashboard documentation
- Test in development environment first
- Use Simple XML reference guide
- Ask questions in repository discussions