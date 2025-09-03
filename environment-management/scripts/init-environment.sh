#!/bin/bash
# Initialize new Splunk environment from baseline template
# Usage: ./init-environment.sh <environment-name>

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENVIRONMENTS_DIR="$REPO_ROOT/environments"
BASELINE_DIR="$ENVIRONMENTS_DIR/baseline"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Validate input
if [ $# -ne 1 ]; then
    error "Usage: $0 <environment-name>"
fi

ENV_NAME="$1"
ENV_DIR="$ENVIRONMENTS_DIR/$ENV_NAME"

# Validate environment name
if [[ ! "$ENV_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    error "Environment name must contain only alphanumeric characters, underscores, and hyphens"
fi

# Check if baseline exists
if [ ! -d "$BASELINE_DIR" ]; then
    error "Baseline environment not found at $BASELINE_DIR"
fi

# Check if environment already exists
if [ -d "$ENV_DIR" ]; then
    warn "Environment '$ENV_NAME' already exists"
    read -p "Do you want to reinitialize it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Aborted by user"
        exit 0
    fi
    log "Removing existing environment..."
    rm -rf "$ENV_DIR"
fi

log "Initializing new environment: $ENV_NAME"

# Create environment directory structure
log "Creating directory structure..."
mkdir -p "$ENV_DIR"/{config,overrides,local,backups}

# Create subdirectories matching baseline structure
mkdir -p "$ENV_DIR/overrides"/{data-models,knowledge-objects,dashboards}
mkdir -p "$ENV_DIR/overrides/knowledge-objects"/{field-extractions,transforms,lookups,macros,eventtypes,tags}
mkdir -p "$ENV_DIR/overrides/dashboards"/{threat-hunting,incident-response,compliance,overview}
mkdir -p "$ENV_DIR/overrides/data-models"/{authentication,network-traffic,malware,vulnerabilities,web,email}

# Create environment configuration file
log "Creating environment configuration..."
cat > "$ENV_DIR/config/environment.conf" << EOF
# $ENV_NAME Environment Configuration
# Inherits from baseline with environment-specific overrides

[environment]
name = $ENV_NAME
type = environment
parent = baseline
description = $ENV_NAME environment configuration
created_date = $(date '+%Y-%m-%d %H:%M:%S')

# Override baseline settings for $ENV_NAME
[indexes]
# Customize retention periods
security_retention = 90
firewall_retention = 180
audit_retention = 365
default_max_data_size = auto_high_volume

[data_models]
# Data model acceleration settings
acceleration_enabled = true
acceleration_earliest_time = -30d@d
acceleration_max_concurrent = 2
acceleration_cron_schedule = 15 1 * * *

[lookups]
# Lookup update frequencies
threat_intel_update_frequency = daily
asset_inventory_update_frequency = weekly
geo_database_update_frequency = monthly

[alerts]
# Alerting configuration
default_severity_threshold = medium
alert_suppression_window = 300
max_alerts_per_hour = 100

[performance]
# Performance tuning
max_searches_per_cpu = 1
search_timeout = 600
dashboard_refresh_interval = 300

[integrations]
# External integration settings
threat_intel_enabled = true
soar_integration_enabled = false
siem_forwarding_enabled = true

[compliance]
# Compliance and audit settings
audit_logging_enabled = true
data_retention_policy_enforced = true
encryption_at_rest_required = false

# Add environment-specific sections here
[$ENV_NAME_specific]
# Environment-only settings
EOF

# Create README file
log "Creating environment README..."
cat > "$ENV_DIR/README.md" << EOF
# $ENV_NAME Environment

This directory contains configurations specific to the $ENV_NAME Splunk environment.

## Environment Information

- **Name**: $ENV_NAME
- **Type**: Splunk Environment
- **Parent**: baseline
- **Created**: $(date '+%Y-%m-%d %H:%M:%S')

## Directory Structure

\`\`\`
$ENV_NAME/
├── config/                    # Environment configuration
│   └── environment.conf       # Main environment config
├── overrides/                # Environment-specific overrides
│   ├── data-models/          # Custom data model configurations
│   ├── knowledge-objects/    # Custom knowledge objects
│   └── dashboards/           # Custom dashboards
├── local/                    # Instance-specific customizations
└── backups/                  # Configuration backups
\`\`\`

## Configuration Precedence

1. **Baseline** (lowest precedence)
2. **Environment Overrides** (this directory)
3. **Local Customizations** (highest precedence)

## Common Tasks

### Add Environment Override
\`\`\`bash
# Copy from baseline and modify
cp ../baseline/path/to/file overrides/path/to/file
# Edit the file to customize for this environment
\`\`\`

### Deploy Environment
\`\`\`bash
# Deploy this environment to Splunk
../../environment-management/scripts/deploy.sh $ENV_NAME
\`\`\`

### Sync from Baseline
\`\`\`bash
# Update this environment with baseline changes
../../environment-management/scripts/sync-baseline.sh $ENV_NAME
\`\`\`

## Environment-Specific Notes

Add any environment-specific information, procedures, or notes here.

### Customizations

Document any customizations made to this environment:
- List of custom dashboards
- Modified knowledge objects
- Environment-specific integrations
- Special configuration requirements

### Deployment Notes

- Splunk instance(s): [list Splunk servers/URLs]
- Deployment method: [manual/automated]
- Special considerations: [any special deployment notes]

## Contacts

- **Environment Owner**: [name/team]
- **Technical Contact**: [name/email]
- **Business Contact**: [name/email]
EOF

# Create .gitkeep files for empty directories
find "$ENV_DIR" -type d -empty -exec touch {}/.gitkeep \;

# Create initial asset inventory if this is not the baseline
if [ "$ENV_NAME" != "baseline" ]; then
    log "Creating environment-specific asset inventory..."
    cat > "$ENV_DIR/overrides/knowledge-objects/lookups/asset_inventory.csv" << EOF
ip,hostname,asset_type,criticality,owner,department,location
# Add $ENV_NAME-specific assets here
# Example:
# 10.0.1.10,$ENV_NAME-server01.local,web_server,medium,$ENV_NAME Team,IT,$ENV_NAME-DataCenter
EOF
fi

# Set appropriate permissions
chmod +x "$ENV_DIR/config/environment.conf"

# Validate the new environment
log "Validating new environment..."
if [ -f "$SCRIPT_DIR/validate-config.sh" ]; then
    "$SCRIPT_DIR/validate-config.sh" "$ENV_NAME" || warn "Validation warnings detected"
else
    warn "Validation script not found, skipping validation"
fi

log "Environment '$ENV_NAME' initialized successfully!"
log "Next steps:"
log "1. Edit $ENV_DIR/config/environment.conf to customize settings"
log "2. Add environment-specific overrides in $ENV_DIR/overrides/"
log "3. Deploy using: $SCRIPT_DIR/deploy.sh $ENV_NAME"
log "4. Update asset inventory and other lookups as needed"

# Summary of created structure
log "Created structure:"
find "$ENV_DIR" -type f | sed "s|$ENV_DIR|  .|g" | sort