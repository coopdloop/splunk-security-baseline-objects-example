#!/bin/bash
# Sync baseline changes to specific environment
# Usage: ./sync-baseline.sh <environment-name> [--dry-run] [--force]

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
FORCE_SYNC=false

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
    echo "  --dry-run    Show what would be synchronized without making changes"
    echo "  --force      Force synchronization even if conflicts detected"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 development                    # Sync baseline to development"
    echo "  $0 production --dry-run          # Preview sync to production"
    echo "  $0 staging --force               # Force sync to staging"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE_SYNC=true
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

# Check if baseline exists
if [ ! -d "$BASELINE_DIR" ]; then
    error "Baseline environment not found at $BASELINE_DIR"
fi

# Don't sync baseline to itself
if [ "$ENV_NAME" = "baseline" ]; then
    error "Cannot sync baseline to itself"
fi

log "Starting baseline sync to environment: $ENV_NAME"
if [ "$DRY_RUN" = true ]; then
    info "DRY RUN MODE - No changes will be made"
fi

# Create backup before sync
if [ "$DRY_RUN" = false ]; then
    BACKUP_DIR="$ENV_DIR/backups/pre-sync-$(date +%Y%m%d-%H%M%S)"
    log "Creating backup at $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Backup existing overrides
    if [ -d "$ENV_DIR/overrides" ]; then
        cp -r "$ENV_DIR/overrides" "$BACKUP_DIR/" 2>/dev/null || warn "Some files could not be backed up"
    fi
    
    # Backup config
    if [ -d "$ENV_DIR/config" ]; then
        cp -r "$ENV_DIR/config" "$BACKUP_DIR/" 2>/dev/null || warn "Config backup incomplete"
    fi
fi

# Function to check for conflicts
check_conflicts() {
    local baseline_file="$1"
    local env_override="$2"
    local relative_path="$3"
    
    if [ -f "$env_override" ]; then
        if ! cmp -s "$baseline_file" "$env_override" 2>/dev/null; then
            warn "Conflict detected: $relative_path (environment has custom version)"
            return 1
        fi
    fi
    return 0
}

# Function to sync file
sync_file() {
    local src_file="$1"
    local dst_file="$2"
    local relative_path="$3"
    local force="$4"
    
    local dst_dir="$(dirname "$dst_file")"
    
    if [ "$DRY_RUN" = true ]; then
        if [ ! -f "$dst_file" ]; then
            info "Would create: $relative_path"
        elif ! cmp -s "$src_file" "$dst_file" 2>/dev/null; then
            if [ "$force" = true ]; then
                info "Would overwrite: $relative_path (forced)"
            else
                warn "Would skip (conflict): $relative_path"
            fi
        else
            info "Already up-to-date: $relative_path"
        fi
        return 0
    fi
    
    # Check for conflicts unless forced
    if [ "$force" = false ] && [ -f "$dst_file" ]; then
        if ! cmp -s "$src_file" "$dst_file" 2>/dev/null; then
            warn "Skipping due to conflict: $relative_path"
            warn "Use --force to overwrite or manually resolve conflicts"
            return 1
        fi
    fi
    
    # Create directory if needed
    mkdir -p "$dst_dir"
    
    # Copy file
    if cp "$src_file" "$dst_file"; then
        log "Synced: $relative_path"
        return 0
    else
        error "Failed to sync: $relative_path"
        return 1
    fi
}

# Sync baseline content to environment
SYNC_ERRORS=0
SYNC_COUNT=0
SKIP_COUNT=0

# Sync directories to monitor
SYNC_DIRS=("data-models" "knowledge-objects" "dashboards" "docs" "examples" "templates")

for dir in "${SYNC_DIRS[@]}"; do
    baseline_dir="$BASELINE_DIR/$dir"
    
    if [ ! -d "$baseline_dir" ]; then
        info "Skipping non-existent baseline directory: $dir"
        continue
    fi
    
    info "Syncing directory: $dir"
    
    # Find all files in baseline directory
    while IFS= read -r -d '' baseline_file; do
        # Get relative path from baseline
        relative_path="${baseline_file#$BASELINE_DIR/}"
        
        # Environment override path
        env_override="$ENV_DIR/overrides/$relative_path"
        
        # Skip if environment has an override and we're not forcing
        if [ -f "$env_override" ] && [ "$FORCE_SYNC" = false ]; then
            if ! cmp -s "$baseline_file" "$env_override" 2>/dev/null; then
                warn "Skipping (environment override exists): $relative_path"
                ((SKIP_COUNT++))
                continue
            fi
        fi
        
        # Sync the file
        if sync_file "$baseline_file" "$env_override" "$relative_path" "$FORCE_SYNC"; then
            ((SYNC_COUNT++))
        else
            ((SYNC_ERRORS++))
        fi
        
    done < <(find "$baseline_dir" -type f -print0)
done

# Sync documentation that might be useful in environment
if [ -f "$BASELINE_DIR/../README.md" ] && [ "$DRY_RUN" = false ]; then
    if [ ! -f "$ENV_DIR/baseline-README.md" ] || [ "$FORCE_SYNC" = true ]; then
        cp "$BASELINE_DIR/../README.md" "$ENV_DIR/baseline-README.md"
        info "Updated baseline README reference"
    fi
fi

# Update sync metadata
if [ "$DRY_RUN" = false ]; then
    SYNC_LOG="$ENV_DIR/config/sync-history.log"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Baseline sync completed. Files: $SYNC_COUNT synced, $SKIP_COUNT skipped, $SYNC_ERRORS errors" >> "$SYNC_LOG"
fi

# Summary
log "Baseline sync completed for environment: $ENV_NAME"
info "Summary:"
info "  Files synced: $SYNC_COUNT"
info "  Files skipped: $SKIP_COUNT"
info "  Errors: $SYNC_ERRORS"

if [ "$DRY_RUN" = true ]; then
    info "This was a dry run - no changes were made"
    info "Run without --dry-run to apply changes"
fi

if [ $SYNC_ERRORS -gt 0 ]; then
    warn "$SYNC_ERRORS errors occurred during sync"
    warn "Check logs above for details"
fi

if [ $SKIP_COUNT -gt 0 ] && [ "$FORCE_SYNC" = false ]; then
    info "$SKIP_COUNT files were skipped due to environment overrides"
    info "Use --force to overwrite environment customizations"
fi

# Validation
if [ "$DRY_RUN" = false ] && [ -f "$SCRIPT_DIR/validate-config.sh" ]; then
    log "Validating environment after sync..."
    if "$SCRIPT_DIR/validate-config.sh" "$ENV_NAME"; then
        log "Environment validation passed"
    else
        warn "Environment validation failed - review configuration"
    fi
fi

if [ $SYNC_ERRORS -eq 0 ]; then
    log "Baseline sync completed successfully!"
    if [ "$DRY_RUN" = false ]; then
        log "Next steps:"
        log "1. Review synced changes in $ENV_DIR/overrides/"
        log "2. Test environment configuration"
        log "3. Deploy if needed: $SCRIPT_DIR/deploy.sh $ENV_NAME"
    fi
else
    error "Baseline sync completed with errors"
fi