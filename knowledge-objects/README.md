# Knowledge Objects

This directory contains Splunk knowledge objects that enhance raw security data with structure, context, and meaning.

## Knowledge Object Types

### Field Extractions
Extract structured fields from raw log data using regular expressions or delimited parsing.

**Location**: `field-extractions/`
**Purpose**: Convert unstructured logs into searchable fields
**File Type**: props.conf configurations

### Transforms
Advanced field processing, lookup definitions, and data manipulation.

**Location**: `transforms/`
**Purpose**: Complex field transformations and lookup table definitions  
**File Type**: transforms.conf configurations

### Lookups
Static and dynamic lookup tables for data enrichment.

**Location**: `lookups/`
**Purpose**: Enrich events with additional context (asset info, threat intel, etc.)
**File Types**: CSV files and lookup definitions

### Macros
Reusable search snippets and parameterized commands.

**Location**: `macros/`
**Purpose**: Standardize common search patterns and simplify complex queries
**File Type**: macros.conf configurations

### Eventtypes
Categorize events based on search criteria.

**Location**: `eventtypes/`
**Purpose**: Group similar events for consistent analysis and reporting
**File Type**: eventtypes.conf configurations

### Tags
Apply semantic labels to events and fields.

**Location**: `tags/`
**Purpose**: Add categorical labels for easier searching and CIM compliance
**File Type**: tags.conf configurations

## Security-Focused Examples

### Common Field Extractions
```ini
# Extract IP addresses
EXTRACT-src_ip = src[_\s]*ip[=:\s]+(?<src_ip>\d+\.\d+\.\d+\.\d+)
EXTRACT-dest_ip = dest[_\s]*ip[=:\s]+(?<dest_ip>\d+\.\d+\.\d+\.\d+)

# Extract usernames
EXTRACT-user = (?i)user[name]*[=:\s]+(?<user>[^\s,]+)

# Extract file hashes
EXTRACT-file_hash = hash[=:\s]+(?<file_hash>[a-fA-F0-9]{32,64})

# Extract URLs
EXTRACT-url = url[=:\s]+(?<url>https?://[^\s]+)
```

### Security Macros
```ini
# High-risk countries
[high_risk_countries]
definition = (src_country="CN" OR src_country="RU" OR src_country="IR" OR src_country="KP")

# Business hours
[business_hours]
definition = (date_hour>=8 AND date_hour<=17 AND date_wday>=2 AND date_wday<=6)

# Critical assets
[critical_assets]
definition = (asset_category="critical" OR asset_type="domain_controller" OR asset_type="database_server")

# Suspicious file extensions
[suspicious_extensions]
definition = (file_ext="exe" OR file_ext="scr" OR file_ext="bat" OR file_ext="ps1")
```

### Threat Intelligence Lookups
```csv
# threat_indicators.csv
threat_indicator,threat_type,confidence,first_seen,description
192.168.1.100,malicious_ip,high,2024-01-01,Known C2 server
malicious.example.com,malicious_domain,medium,2024-01-02,Phishing domain
abc123def456,file_hash,high,2024-01-03,Ransomware payload
```

### Security Event Types
```ini
[authentication_success]
search = tag=authentication action=success

[authentication_failure]  
search = tag=authentication action=failure

[malware_detected]
search = tag=malware (action=blocked OR action=quarantined)

[network_intrusion]
search = tag=intrusion severity=high

[web_attack]
search = tag=attack (sourcetype=access_* OR tag=web)

[data_exfiltration]
search = tag=network bytes_out>1000000 NOT dest_category=internal
```

## Organization by Security Domain

### Network Security
- Firewall field extractions
- IDS/IPS parsing rules
- Network flow analysis
- DNS security monitoring

### Endpoint Security
- Antivirus log parsing
- EDR field extractions
- Process monitoring
- File integrity monitoring

### Identity & Access
- Authentication log parsing
- Directory service monitoring
- Privilege escalation detection
- Access review automation

### Web Security
- Web server log parsing
- Proxy log analysis
- Web application firewall rules
- URL categorization

## Deployment Workflow

1. **Development**: Create and test knowledge objects
2. **Validation**: Verify field extractions and CIM compliance
3. **Documentation**: Document configuration and use cases
4. **Staging**: Deploy to test environment
5. **Production**: Roll out to production Splunk environment

## Quick Start Commands

### Test Field Extractions
```spl
# Test regex extraction
| makeresults | eval _raw="user=john.doe src_ip=192.168.1.100" 
| rex field=_raw "user=(?<user>\w+\.\w+)" 
| table user

# Validate existing extraction
index=security sourcetype=your_sourcetype | head 100 | table _raw, extracted_field
```

### Lookup Testing
```spl
# Test lookup enrichment
| makeresults | eval ip="192.168.1.100" 
| lookup threat_indicators threat_indicator AS ip 
| table ip, threat_type, confidence
```

### Macro Usage
```spl
# Use security macro
index=security `high_risk_countries` `business_hours`
| stats count by src_country, date_hour
```

For detailed implementation examples, explore the specific knowledge object type folders.