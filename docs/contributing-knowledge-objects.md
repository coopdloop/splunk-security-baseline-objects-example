# Contributing Knowledge Objects

This guide covers contributing Splunk knowledge objects including field extractions, transforms, lookups, macros, eventtypes, and tags.

## Overview

Knowledge objects enhance raw data by adding context, structure, and meaning. They are essential for making security data actionable and searchable.

## Structure

```
knowledge-objects/
├── field-extractions/   # Props.conf field extraction rules
├── transforms/         # Transforms.conf advanced parsing
├── lookups/           # Lookup tables and definitions
├── macros/            # Reusable search macros
├── eventtypes/        # Event type classifications
└── tags/              # Tag assignments for categorization
```

## Contributing Guidelines

### 1. Field Extractions

Location: `knowledge-objects/field-extractions/`

#### File Naming
`<vendor>_<product>_props.conf`

#### Structure
```ini
[vendor:product:sourcetype]
# Basic field extraction
EXTRACT-username = (?i)user[=:\s]+(?<user>\w+)
EXTRACT-src_ip = src_ip[=:\s]+(?<src_ip>\d+\.\d+\.\d+\.\d+)

# Calculated fields for CIM compliance
EVAL-vendor_product = "Vendor Product Name"
EVAL-severity = case(priority=="high","critical", priority=="medium","medium", priority=="low","informational")

# Field aliases for CIM compliance
FIELDALIAS-dest_ip = destination_ip AS dest_ip
FIELDALIAS-source_ip = source_address AS src_ip
```

#### Best Practices
- Use named capture groups
- Make regex case-insensitive with `(?i)`
- Test extractions with sample data
- Follow CIM field naming conventions

### 2. Transforms

Location: `knowledge-objects/transforms/`

#### File Naming
`<vendor>_<product>_transforms.conf`

#### Structure
```ini
# Lookup table definition
[threat_intel_lookup]
filename = threat_indicators.csv
case_sensitive_match = false

# Regex transformation
[extract_malware_hash]
REGEX = hash[=:\s]+(?<file_hash>[a-fA-F0-9]{32,64})
FORMAT = file_hash::$1

# Sedcmd for data cleanup
[remove_sensitive_data]
REGEX = (password|token)[=:\s]+\S+
FORMAT = $1=***REDACTED***
```

### 3. Lookups

Location: `knowledge-objects/lookups/`

#### CSV Lookup Files
- `threat_indicators.csv` - IOC enrichment
- `asset_inventory.csv` - Asset information
- `user_roles.csv` - User role mappings
- `severity_mapping.csv` - Severity standardization

#### Lookup Definition Files
`<category>_lookups.conf`

```ini
[threat_intel_iocs]
filename = threat_indicators.csv
case_sensitive_match = false
match_type = WILDCARD(threat_indicator)
```

### 4. Macros

Location: `knowledge-objects/macros/`

#### File Naming
`<category>_macros.conf`

#### Examples
```ini
# Security-focused macros
[security_sourcetypes]
definition = (sourcetype=firewall OR sourcetype=ids OR sourcetype=av)

[threat_hunting_timeframe]
definition = earliest=-30d@d latest=now

[high_risk_countries]
definition = (src_country="CN" OR src_country="RU" OR src_country="IR" OR src_country="KP")

# Parameterized macro
[user_activity(1)]
args = username
definition = index=security user="$username$" | stats count by _time, action, src_ip
```

### 5. Eventtypes

Location: `knowledge-objects/eventtypes/`

#### File Naming
`<category>_eventtypes.conf`

#### Structure
```ini
[authentication_success]
search = tag=authentication action=success

[authentication_failure] 
search = tag=authentication action=failure

[malware_detected]
search = tag=malware signature!=""

[network_intrusion]
search = tag=intrusion severity=high

[web_attack]
search = tag=attack (sourcetype=access_* OR sourcetype=iis)
```

### 6. Tags

Location: `knowledge-objects/tags/`

#### File Naming
`<category>_tags.conf`

#### Structure
```ini
[eventtype=authentication_success]
authentication = enabled
success = enabled

[eventtype=authentication_failure]
authentication = enabled
failure = enabled

[eventtype=malware_detected]
malware = enabled
alert = enabled

[eventtype=network_intrusion]
intrusion = enabled
attack = enabled
network = enabled
```

## Knowledge Object Templates

### Field Extraction Template
```ini
[your:sourcetype]
# Timestamp extraction
TIME_PREFIX = timestamp[=:\s]+
TIME_FORMAT = %Y-%m-%d %H:%M:%S
MAX_TIMESTAMP_LOOKAHEAD = 25

# Field extractions
EXTRACT-user = user[=:\s]+(?<user>[^,\s]+)
EXTRACT-action = action[=:\s]+(?<action>\w+)
EXTRACT-src_ip = src[=:\s]+(?<src_ip>\d+\.\d+\.\d+\.\d+)

# CIM compliance
EVAL-vendor_product = "Your Vendor Product"
FIELDALIAS-dest = destination AS dest
```

### Lookup Integration Template
```ini
[your:sourcetype]
LOOKUP-asset_enrichment = asset_inventory ip AS src_ip OUTPUTNEW asset_type, criticality, owner
LOOKUP-threat_intel = threat_indicators ip AS src_ip OUTPUTNEW threat_category, confidence, first_seen
```

## Validation Checklist

Before contributing knowledge objects:

- [ ] Field extractions tested with sample data
- [ ] CIM field mappings validated
- [ ] Lookup tables properly formatted
- [ ] Macros tested in search interface
- [ ] Eventtypes return expected results
- [ ] Tags applied correctly
- [ ] Performance impact assessed
- [ ] Documentation complete

## Performance Considerations

- Use specific sourcetypes in extractions
- Avoid overly complex regex patterns
- Test lookup performance with large datasets
- Consider search-time vs. index-time extractions
- Monitor resource usage after deployment

## Need Help?

- Review examples in each subfolder
- Check Splunk documentation for knowledge object types
- Test configurations in a development environment first
- Ask questions in repository discussions