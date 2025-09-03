# Multi-Environment Splunk TA Management

This directory structure supports managing Splunk Technical Add-ons across multiple environments with inheritance from a baseline template.

## Environment Structure

```
environments/
├── baseline/                 # Core template - inherited by all environments
│   ├── data-models/         # Standard CIM data models
│   ├── knowledge-objects/   # Common knowledge objects
│   ├── dashboards/         # Standard dashboards
│   └── config/             # Base configuration
├── development/            # Development environment overrides
│   ├── overrides/          # Dev-specific configurations
│   ├── config/            # Environment config
│   └── local/             # Local customizations
├── staging/               # Staging environment overrides
│   ├── overrides/         # Staging-specific configurations
│   ├── config/           # Environment config
│   └── local/            # Local customizations
└── production/           # Production environment overrides
    ├── overrides/        # Prod-specific configurations
    ├── config/          # Environment config
    └── local/           # Local customizations
```

## Inheritance Model

### Baseline Environment
- Contains all standard configurations
- CIM-compliant data models
- Common knowledge objects
- Standard dashboards and saved searches
- Shared lookups and macros

### Environment-Specific Overrides
Each environment inherits from baseline and can override:
- Configuration values (indexes, retention, etc.)
- Environment-specific lookups (asset inventories, user lists)
- Custom dashboards and alerts
- Performance tuning parameters
- Integration endpoints and credentials

## Configuration Precedence

1. **Baseline** - Core configurations (lowest precedence)
2. **Environment Overrides** - Environment-specific modifications
3. **Local** - Instance-specific customizations (highest precedence)

## Quick Start

### 1. Initialize New Environment
```bash
./environment-management/scripts/init-environment.sh <environment-name>
```

### 2. Deploy to Environment  
```bash
./environment-management/scripts/deploy.sh <environment-name>
```

### 3. Sync from Baseline
```bash
./environment-management/scripts/sync-baseline.sh <environment-name>
```

## Environment Management

### Adding New Environment
1. Create environment directory: `mkdir environments/new-env`
2. Copy baseline structure: `cp -r environments/baseline/* environments/new-env/`
3. Configure environment-specific settings
4. Test deployment in isolated environment

### Updating Baseline
1. Make changes to `environments/baseline/`
2. Test changes in development environment
3. Use sync scripts to propagate to other environments
4. Validate each environment after sync

### Environment-Specific Customizations
- Store in `environments/<env>/overrides/`
- Use same directory structure as baseline
- Files in overrides take precedence over baseline
- Document all customizations in environment README

For detailed management procedures, see [Environment Management Guide](../environment-management/README.md).