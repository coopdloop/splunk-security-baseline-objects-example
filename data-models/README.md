# Data Models

This directory contains CIM-compliant data model configurations for security use cases.

## Common Information Model (CIM) Overview

The Splunk Common Information Model provides a standardized way to normalize security data across different vendors and technologies. CIM compliance ensures:

- Consistent field naming across data sources
- Compatibility with Splunk Enterprise Security
- Interoperability between security apps
- Accelerated search performance through data models

## Available Data Models

### Authentication
**Purpose**: User authentication events, login attempts, privilege escalation
**Key Fields**: user, src_ip, dest, action, app, authentication_method
**Use Cases**: Failed login monitoring, privilege abuse detection, SSO analysis

### Network Traffic  
**Purpose**: Network connections, firewall logs, traffic analysis
**Key Fields**: src_ip, dest_ip, src_port, dest_port, protocol, action, bytes
**Use Cases**: Network intrusion detection, traffic analysis, firewall monitoring

### Malware
**Purpose**: Malware detection, file analysis, antivirus alerts
**Key Fields**: file_hash, file_name, signature, vendor_product, action
**Use Cases**: Malware tracking, IOC correlation, endpoint protection monitoring

### Vulnerabilities
**Purpose**: Vulnerability scan results, patch management, risk assessment
**Key Fields**: dest, severity, cve, category, vendor_product
**Use Cases**: Vulnerability management, patch prioritization, risk reporting

### Web
**Purpose**: Web server logs, proxy logs, web application security
**Key Fields**: url, uri_path, http_method, status, src_ip, user
**Use Cases**: Web attack detection, access monitoring, application security

### Email
**Purpose**: Email security events, phishing detection, attachment analysis
**Key Fields**: recipient, sender, subject, attachment_type, action
**Use Cases**: Phishing detection, email security monitoring, DLP

## CIM Field Mapping Guide

### Standard Fields (All Data Models)
```
_time          # Event timestamp
host           # Source host/device
source         # Log source
sourcetype     # Splunk sourcetype
index          # Splunk index
vendor_product # "Vendor Product Name"
```

### Authentication Data Model
```
user           # Username/account
src            # Source IP or system
dest           # Destination system
action         # success, failure
app            # Application name
authentication_method  # Method used (LDAP, SAML, etc.)
duration       # Session duration
reason         # Failure reason
signature      # Authentication signature/rule
```

### Network Traffic Data Model
```
src_ip, src_port      # Source IP and port
dest_ip, dest_port    # Destination IP and port
protocol              # Network protocol (TCP, UDP, ICMP)
action               # allowed, blocked, teardown
bytes_in, bytes_out  # Traffic volume
packets_in, packets_out  # Packet counts
direction            # inbound, outbound
transport            # Transport protocol
vlan                 # VLAN information
```

### Data Model Acceleration

Enable acceleration for faster searches:

```ini
[YourDataModel]
acceleration = true
acceleration.earliest_time = -1mon@mon
acceleration.max_concurrent = 2
acceleration.max_time = 3600
```

## Quick Reference

### Essential CIM Commands
```spl
# List available data models
| rest /services/data/models

# Search specific data model
| datamodel Authentication search

# Pivot using data model
| pivot Authentication Authentication count(Authentication) AS "Event Count" SPLITROW user

# Validate CIM compliance
| datamodel Authentication search | eval cim_compliant=if(isnotnull(user) AND isnotnull(action),"yes","no")
```

### Field Validation
```spl
# Check field population
| datamodel YourDataModel search
| stats count, dc(field_name) by sourcetype
| eval population_rate=count/total_events*100

# Verify CIM field mappings
| datamodel Authentication search
| table user, src, dest, action, app
| head 100
```

## Best Practices

### Data Model Design
- Start with CIM-required fields
- Add vendor-specific fields as calculated fields
- Use field aliases for existing field names
- Implement proper time extraction
- Tag events appropriately

### Performance Optimization
- Enable selective data model acceleration
- Use appropriate time ranges for acceleration
- Monitor acceleration storage usage
- Optimize field extractions
- Consider search-time vs. index-time processing

### Documentation Requirements
Each data model must include:
- Field mapping documentation
- Sample events and extractions
- Known limitations or issues
- Performance considerations
- Testing procedures

## Getting Started

1. Choose your data model category
2. Review existing examples in the folder
3. Follow the CIM field reference
4. Test with sample data
5. Document your configuration
6. Submit for review

For detailed implementation examples, see the specific data model folders.