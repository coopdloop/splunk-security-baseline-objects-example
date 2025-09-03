#!/bin/bash
# Deploy environment configuration to Splunk
# Usage: ./deploy.sh <environment-name> [--dry-run] [--component=<component>]

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
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
DRY_RUN=false
COMPONENT=""

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Usage function
usage() {
    echo "Usage: $0 <environment-name> [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run              Show what would be deployed without making changes"
    echo "  --component=<name>     Deploy only specific component (data-models, knowledge-objects, dashboards)"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 production                               # Full deployment to production"
    echo "  $0 development --dry-run                    # Preview deployment to development"  
    echo "  $0 staging --component=dashboards           # Deploy only dashboards to staging"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --component=*)
            COMPONENT="${1#*=}"
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            ;;
        *)
            if [ -z "$ENV_NAME" ]; then
                ENV_NAME="$1"
            else
                error "Multiple environment names specified"
            fi
            shift
            ;;
    esac
done

# Validate input
if [ -z "$ENV_NAME" ]; then
    usage
    error "Environment name required"
fi

ENV_DIR="$ENVIRONMENTS_DIR/$ENV_NAME"

# Validate environment exists
if [ ! -d "$ENV_DIR" ]; then
    error "Environment '$ENV_NAME' not found at $ENV_DIR"
fi

# Load environment configuration
ENV_CONFIG="$ENV_DIR/config/environment.conf"
if [ ! -f "$ENV_CONFIG" ]; then
    error "Environment configuration not found: $ENV_CONFIG"
fi

log "Starting deployment for environment: $ENV_NAME"
if [ "$DRY_RUN" = true ]; then
    info "DRY RUN MODE - No changes will be made"
fi

if [ -n "$COMPONENT" ]; then
    info "Deploying component: $COMPONENT"
fi

# Read deployment configuration
DEPLOYMENT_CONFIG="$SCRIPT_DIR/../configs/deployment.conf"
if [ -f "$DEPLOYMENT_CONFIG" ]; then
    source "$DEPLOYMENT_CONFIG"
fi

# Create deployment package directory
DEPLOY_DIR="/tmp/splunk-deploy-$$"
PACKAGE_DIR="$DEPLOY_DIR/security_ta_repo"

if [ "$DRY_RUN" = false ]; then
    log "Creating deployment package in $DEPLOY_DIR"
    mkdir -p "$PACKAGE_DIR"/{default,metadata,lookups}
fi

# Function to merge configurations
merge_config() {
    local config_type="$1"
    local output_file="$2"
    
    local baseline_file="$BASELINE_DIR/$config_type"
    local override_file="$ENV_DIR/overrides/$config_type"
    local local_file="$ENV_DIR/local/$config_type"
    
    if [ "$DRY_RUN" = true ]; then
        info "Would merge $config_type:"
        [ -f "$baseline_file" ] && info "  - Baseline: $baseline_file"
        [ -f "$override_file" ] && info "  - Override: $override_file" 
        [ -f "$local_file" ] && info "  - Local: $local_file"
        return 0
    fi
    
    local temp_file="$output_file.tmp"
    
    # Start with baseline if it exists
    if [ -f "$baseline_file" ]; then
        cp "$baseline_file" "$temp_file"
    else
        touch "$temp_file"
    fi
    
    # Apply overrides (simple concatenation for now)
    if [ -f "$override_file" ]; then
        echo "" >> "$temp_file"
        echo "# Environment-specific overrides for $ENV_NAME" >> "$temp_file"
        cat "$override_file" >> "$temp_file"
    fi
    
    # Apply local customizations
    if [ -f "$local_file" ]; then
        echo "" >> "$temp_file" 
        echo "# Local customizations for $ENV_NAME" >> "$temp_file"
        cat "$local_file" >> "$temp_file"
    fi
    
    mv "$temp_file" "$output_file"
    log "Merged $config_type"
}

# Function to deploy component
deploy_component() {
    local component="$1"
    local deploy_count=0
    
    info "Deploying component: $component"
    
    case "$component" in
        "knowledge-objects")
            # Deploy props.conf
            if [ -f "$BASELINE_DIR/knowledge-objects/field-extractions/"*.conf ] || 
               [ -f "$ENV_DIR/overrides/knowledge-objects/field-extractions/"*.conf ]; then
                merge_config "knowledge-objects/field-extractions/props.conf" "$PACKAGE_DIR/default/props.conf"
                ((deploy_count++))
            fi
            
            # Deploy transforms.conf  
            if [ -f "$BASELINE_DIR/knowledge-objects/transforms/"*.conf ] ||
               [ -f "$ENV_DIR/overrides/knowledge-objects/transforms/"*.conf ]; then
                merge_config "knowledge-objects/transforms/transforms.conf" "$PACKAGE_DIR/default/transforms.conf"
                ((deploy_count++))
            fi
            
            # Deploy macros.conf
            if [ -f "$BASELINE_DIR/knowledge-objects/macros/"*.conf ] ||
               [ -f "$ENV_DIR/overrides/knowledge-objects/macros/"*.conf ]; then
                merge_config "knowledge-objects/macros/macros.conf" "$PACKAGE_DIR/default/macros.conf"
                ((deploy_count++))
            fi
            
            # Deploy eventtypes.conf
            if [ -f "$BASELINE_DIR/knowledge-objects/eventtypes/"*.conf ] ||
               [ -f "$ENV_DIR/overrides/knowledge-objects/eventtypes/"*.conf ]; then
                merge_config "knowledge-objects/eventtypes/eventtypes.conf" "$PACKAGE_DIR/default/eventtypes.conf"
                ((deploy_count++))
            fi
            
            # Deploy tags.conf
            if [ -f "$BASELINE_DIR/knowledge-objects/tags/"*.conf ] ||
               [ -f "$ENV_DIR/overrides/knowledge-objects/tags/"*.conf ]; then
                merge_config "knowledge-objects/tags/tags.conf" "$PACKAGE_DIR/default/tags.conf"
                ((deploy_count++))
            fi
            
            # Deploy lookup files
            for lookup_dir in "$BASELINE_DIR/knowledge-objects/lookups" "$ENV_DIR/overrides/knowledge-objects/lookups"; do
                if [ -d "$lookup_dir" ]; then
                    find "$lookup_dir" -name "*.csv" -exec cp {} "$PACKAGE_DIR/lookups/" \; 2>/dev/null || true
                fi
            done
            ;;
            
        "data-models")
            if [ -f "$BASELINE_DIR/data-models/"*".conf" ] ||
               [ -f "$ENV_DIR/overrides/data-models/"*".conf" ]; then
                merge_config "data-models/datamodels.conf" "$PACKAGE_DIR/default/datamodels.conf"
                ((deploy_count++))
            fi
            ;;
            
        "dashboards")  
            # Deploy saved searches
            if [ -f "$BASELINE_DIR/dashboards/"*"/savedsearches.conf" ] ||
               [ -f "$ENV_DIR/overrides/dashboards/"*"/savedsearches.conf" ]; then
                merge_config "dashboards/savedsearches.conf" "$PACKAGE_DIR/default/savedsearches.conf"
                ((deploy_count++))
            fi
            
            # Deploy dashboard XML files (these require manual Splunk import)
            local dashboard_dir="$DEPLOY_DIR/dashboards"
            mkdir -p "$dashboard_dir"
            
            for dash_dir in "$BASELINE_DIR/dashboards" "$ENV_DIR/overrides/dashboards"; do
                if [ -d "$dash_dir" ]; then
                    find "$dash_dir" -name "*.xml" -exec cp {} "$dashboard_dir/" \; 2>/dev/null || true
                fi
            done
            ;;
    esac
    
    return $deploy_count
}

# Create app.conf
if [ "$DRY_RUN" = false ]; then
    cat > "$PACKAGE_DIR/default/app.conf" << EOF
[install]
is_configured = true
state = enabled

[ui]
is_visible = true
label = Security TA Repository - $ENV_NAME

[launcher]
author = Security Engineering Team
version = 1.0.0
description = Deployed configuration for $ENV_NAME environment

[package]
id = security_ta_repo_$ENV_NAME
check_for_updates = false
EOF
fi

# Create metadata
if [ "$DRY_RUN" = false ]; then
    cat > "$PACKAGE_DIR/metadata/default.meta" << EOF
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
EOF
fi

# Deploy components
TOTAL_DEPLOYED=0

if [ -n "$COMPONENT" ]; then
    # Deploy specific component
    deploy_component "$COMPONENT"
    TOTAL_DEPLOYED=$?
else
    # Deploy all components
    for comp in "knowledge-objects" "data-models" "dashboards"; do
        deploy_component "$comp"
        ((TOTAL_DEPLOYED += $?))
    done
fi

# Create deployment summary
if [ "$DRY_RUN" = false ]; then
    cat > "$DEPLOY_DIR/deployment-summary.txt" << EOF
Splunk TA Repository Deployment Summary
======================================

Environment: $ENV_NAME
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
Components Deployed: $TOTAL_DEPLOYED
Package Location: $PACKAGE_DIR

Deployment Instructions:
1. Copy the security_ta_repo directory to \$SPLUNK_HOME/etc/apps/
2. Restart Splunk or reload configurations
3. Import dashboard XML files manually if deploying dashboards
4. Verify data model acceleration settings
5. Test knowledge object functionality

Manual Steps Required:
- Dashboard XML import via Splunk Web UI
- Data model acceleration configuration  
- Index configuration (if needed)
- Lookup file permissions

For environment-specific settings, refer to:
$ENV_CONFIG
EOF

    log "Deployment package created successfully"
    log "Package location: $PACKAGE_DIR"
    log "Summary: $DEPLOY_DIR/deployment-summary.txt"
    
    if [ -n "$SPLUNK_HOME" ]; then
        read -p "Deploy directly to Splunk at $SPLUNK_HOME? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Deploying to Splunk..."
            cp -r "$PACKAGE_DIR" "$SPLUNK_HOME/etc/apps/"
            log "Deployment completed. Restart Splunk to apply changes."
        fi
    fi
    
    log "To deploy manually:"
    log "  cp -r $PACKAGE_DIR \$SPLUNK_HOME/etc/apps/"
    log "  \$SPLUNK_HOME/bin/splunk restart"
    
else
    log "Dry run completed. No deployment package created."
fi

log "Deployment process completed for environment: $ENV_NAME"

# Cleanup on exit
trap 'rm -rf "$DEPLOY_DIR"' EXIT