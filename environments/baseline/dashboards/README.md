# Security Dashboards

This directory contains pre-built security dashboards and saved searches for threat hunting, incident response, compliance monitoring, and operational oversight.

## Dashboard Categories

### Threat Hunting
**Location**: `threat-hunting/`
**Purpose**: Proactive security monitoring and threat detection
**Key Features**:
- Anomaly detection dashboards
- IOC correlation and tracking
- Behavioral analysis and baselining
- Threat intelligence integration

### Incident Response
**Location**: `incident-response/`
**Purpose**: Support security incident investigation and response
**Key Features**:
- Timeline reconstruction
- Asset impact assessment
- Evidence collection workflows
- Lateral movement tracking

### Compliance
**Location**: `compliance/`
**Purpose**: Regulatory and framework compliance monitoring
**Key Features**:
- NIST Cybersecurity Framework
- PCI DSS monitoring
- GDPR privacy compliance
- SOX audit trails

### Overview
**Location**: `overview/`
**Purpose**: Executive summaries and operational metrics
**Key Features**:
- Security posture overview
- Threat landscape summary
- Operational efficiency metrics
- Executive reporting

## Dashboard Structure

Each dashboard category follows this structure:
```
category-name/
├── README.md                    # Category overview
├── dashboard-name/              # Individual dashboard folder
│   ├── dashboard.xml           # Simple XML dashboard
│   ├── savedsearches.conf      # Associated saved searches
│   ├── README.md               # Dashboard documentation
│   ├── queries.spl             # SPL queries used
│   └── screenshots/            # Visual examples
└── shared/                     # Shared components
    ├── macros.conf             # Category-specific macros
    └── lookups/                # Category-specific lookups
```

## Key Security Use Cases

### 1. Threat Detection
```spl
# DNS Tunneling Detection
index=network sourcetype=dns
| stats count, dc(answer) as unique_answers, avg(len(query)) as avg_length by query
| where unique_answers > 10 AND avg_length > 50

# Suspicious Process Execution
index=endpoint sourcetype=sysmon EventCode=1
| rare Image limit=10
| where count < 5 AND probability < 0.01

# Lateral Movement Detection  
| datamodel Authentication search
| stats dc(dest) as unique_systems by user
| where unique_systems > 10
```

### 2. Incident Response
```spl
# Compromise Timeline
index=* user="$compromised_user$"
| eval category=case(
    match(sourcetype,"auth"),"Authentication",
    match(sourcetype,"web"),"Web Activity",
    match(sourcetype,"network"),"Network",
    1=1,"Other"
)
| table _time, category, src_ip, dest_ip, action, details
| sort _time

# Asset Impact Assessment
index=network dest_ip="$compromised_ip$"
| stats count by src_ip, dest_port, action
| lookup asset_inventory ip AS src_ip OUTPUTNEW asset_type, criticality
| where criticality="high"
```

### 3. Compliance Monitoring
```spl
# Access Review Report
| datamodel Authentication search
| where action="success"
| stats latest(_time) as last_access by user, dest
| eval days_since_access=round((now()-last_access)/86400,0)
| where days_since_access > 90

# Data Access Monitoring
index=database sourcetype=audit_trail
| lookup sensitive_data_inventory table_name OUTPUTNEW classification, data_type
| where classification="PCI" OR classification="PII"
| stats count by user, table_name, operation
```

## Dashboard Components

### Interactive Time Controls
```xml
<input type="time" token="time_picker">
  <label>Time Range</label>
  <default>
    <earliest>-24h@h</earliest>
    <latest>now</latest>
  </default>
</input>
```

### Dynamic Filtering
```xml
<input type="dropdown" token="severity_filter">
  <label>Severity Level</label>
  <choice value="*">All Severities</choice>
  <choice value="critical">Critical</choice>
  <choice value="high">High</choice>
  <choice value="medium">Medium</choice>
  <choice value="low">Low</choice>
  <default>*</default>
</input>
```

### Key Visualizations

#### Single Value Displays
- Critical alert counts
- SLA compliance percentages
- Risk scores
- Threat levels

#### Time Series Charts
- Event trends over time
- Attack patterns
- User activity patterns
- System performance metrics

#### Geographic Maps
- Attack source locations
- Global threat distribution
- Regional compliance status
- Data flow visualization

#### Statistical Charts
- Top attackers/targets
- Most common vulnerabilities
- User risk rankings
- Asset criticality distribution

## Saved Search Patterns

### Alerting Searches
```ini
[Critical Security Alert]
search = index=security severity=critical
| stats count by threat_type, src_ip
| where count > threshold
cron_schedule = */5 * * * *
alert.track = 1
```

### Summary Searches
```ini
[Daily Security Summary]  
search = index=security
| bucket _time span=1d
| stats count by _time, category
| eval date=strftime(_time,"%Y-%m-%d")
cron_schedule = 0 1 * * *
```

### Reporting Searches
```ini
[Weekly Threat Intelligence Report]
search = | datamodel Malware search
| stats count by signature, vendor_product
| sort -count | head 20
cron_schedule = 0 9 * * 1
```

## Performance Guidelines

### Search Optimization
- Use specific time ranges
- Filter by index early
- Leverage data model acceleration
- Minimize regex complexity
- Use statistical commands efficiently

### Dashboard Performance
- Limit concurrent panel searches
- Use appropriate refresh intervals
- Implement search result caching
- Optimize drilldown queries
- Monitor resource usage

## World of Possibilities for Splunk Security Knowledge

### Advanced Analytics
- **Machine Learning**: Anomaly detection, clustering, outlier identification
- **Statistical Analysis**: Trend analysis, correlation studies, predictive modeling
- **Behavioral Analytics**: User behavior baselines, deviation detection

### Integration Capabilities
- **SOAR Platforms**: Phantom, Demisto integration
- **Threat Intelligence**: STIX/TAXII feeds, commercial threat intel
- **External APIs**: VirusTotal, URLVoid, IP reputation services
- **Ticketing Systems**: ServiceNow, JIRA integration

### Advanced Use Cases
- **Threat Hunting**: Hypothesis-driven investigations
- **Digital Forensics**: Evidence collection and analysis
- **Compliance Automation**: Automated compliance reporting
- **Risk Assessment**: Quantitative risk analysis
- **Security Metrics**: KPI tracking and measurement

### Data Science Applications
- **Predictive Security**: Predicting attack likelihood
- **Risk Scoring**: Dynamic risk assessment algorithms
- **Fraud Detection**: Financial fraud pattern recognition
- **Insider Threat**: Behavioral anomaly detection

### Visualization Possibilities
- **3D Network Topology**: Interactive network visualization
- **Geospatial Analysis**: Attack mapping and origin tracking
- **Timeline Analysis**: Attack chain reconstruction
- **Relationship Mapping**: Entity relationship visualization

### Automation Opportunities
- **Automated Response**: Programmatic response to threats
- **Alert Enrichment**: Automatic context addition
- **Report Generation**: Scheduled executive reporting
- **Data Collection**: Automated log ingestion and parsing

Explore the specific folders for implementation examples and detailed documentation.