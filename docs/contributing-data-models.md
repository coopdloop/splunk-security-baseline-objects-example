# Contributing Data Models

This guide covers contributing CIM-compliant data model configurations for security use cases.

## Overview

Data models in Splunk provide a structured way to organize and accelerate searches across security data. This repository focuses on CIM (Common Information Model) compliance for Enterprise Security integration.

## Structure

```
data-models/
├── authentication/     # User authentication events
├── network-traffic/   # Network connection and traffic data
├── malware/          # Malware detection and analysis
├── vulnerabilities/  # Vulnerability scan results
├── web/             # Web server and proxy logs
└── email/           # Email security events
```

## Contributing Guidelines

### 1. Choose Your Data Model Category

Select the appropriate folder based on your data source:
- **authentication/**: Login events, SSO, privileged access
- **network-traffic/**: Firewall logs, network flows, DNS
- **malware/**: AV alerts, sandboxing results, file analysis
- **vulnerabilities/**: Scan results, patch management, assessments
- **web/**: Web server logs, proxy logs, web application security
- **email/**: Email security, phishing, attachment analysis

### 2. File Naming Convention

Use this format: `<vendor>_<product>_<version>.conf`

Examples:
- `palo_alto_firewall_v1.conf`
- `crowdstrike_falcon_v2.conf`
- `microsoft_defender_v1.conf`

### 3. Required Components

Each data model contribution must include:

#### datamodels.conf
```ini
[YourDataModel]
acceleration = true
acceleration.earliest_time = -1mon
acceleration.max_concurrent = 2
```

#### props.conf (CIM field mapping)
```ini
[your:sourcetype]
EVAL-vendor_product = "Vendor Product Name"
EVAL-dest = coalesce(destination_ip, dest_ip)
EVAL-src = coalesce(source_ip, src_ip)
```

#### transforms.conf (if needed)
```ini
[extract_custom_fields]
REGEX = your_regex_pattern
FORMAT = field1::$1 field2::$2
```

### 4. CIM Compliance Checklist

- [ ] Maps to appropriate CIM data model
- [ ] Uses standard field names (src, dest, user, action, etc.)
- [ ] Includes vendor_product field
- [ ] Tags applied correctly
- [ ] Event types defined

### 5. Documentation Template

Include a README.md in your data model folder:

```markdown
# Vendor Product Name Data Model

## Overview
Brief description of the data source and security use cases.

## CIM Compliance
- **Data Model**: Authentication/Network Traffic/etc.
- **Required Fields**: List of CIM fields populated
- **Optional Fields**: Additional fields available

## Installation
1. Copy configurations to appropriate Splunk directories
2. Restart Splunk or reload configurations
3. Verify data model acceleration

## Sample Searches
```spl
| datamodel Authentication search | head 100
```

## Known Issues
- List any limitations or known issues
```

### 6. Testing Your Configuration

Before submitting:
1. Validate field extractions work correctly
2. Confirm CIM compliance using data model pivot
3. Test with sample data if available
4. Document any performance considerations

## CIM Field Reference

### Common Fields Across All Data Models
- `_time` - Event timestamp
- `host` - Source host
- `source` - Data source
- `sourcetype` - Splunk sourcetype
- `index` - Splunk index

### Authentication Data Model
- `user` - Username
- `dest` - Destination system
- `src` - Source IP/system
- `action` - success/failure
- `app` - Application name

### Network Traffic Data Model
- `src_ip`, `dest_ip` - IP addresses
- `src_port`, `dest_port` - Port numbers
- `protocol` - Network protocol
- `bytes_in`, `bytes_out` - Traffic volume
- `action` - allowed/blocked

### Web Data Model
- `url` - Full URL
- `uri_path` - URI path
- `http_method` - GET/POST/etc.
- `status` - HTTP status code
- `src_ip` - Client IP

## Need Help?

- Check existing examples in the folder
- Reference [Splunk CIM Documentation](https://docs.splunk.com/Documentation/CIM/latest/User/Overview)
- Ask questions in repository discussions