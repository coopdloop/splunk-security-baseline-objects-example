# Environment Management

This directory contains tools and documentation for managing multiple Splunk environments with inheritance from a baseline template.

## Overview

The multi-environment approach allows you to:
- Maintain consistent configurations across environments
- Apply environment-specific customizations
- Easily propagate updates from baseline to all environments  
- Track configuration drift and changes
- Manage deployments systematically

## Directory Structure

```
environment-management/
├── README.md                    # This file
├── scripts/                     # Automation scripts
│   ├── init-environment.sh      # Initialize new environment
│   ├── deploy.sh               # Deploy to environment
│   ├── sync-baseline.sh        # Sync baseline changes
│   ├── validate-config.sh      # Validate configurations
│   └── compare-environments.sh # Compare environment configs
├── configs/                    # Management configurations
│   ├── deployment.conf         # Deployment settings
│   └── validation.conf         # Validation rules
└── templates/                  # Environment templates
    ├── environment.conf.template
    └── override-structure/
```

## Environment Inheritance Model

### Baseline Template
- **Location**: `environments/baseline/`
- **Purpose**: Core configurations shared across all environments
- **Contents**: Standard data models, knowledge objects, dashboards, lookups

### Environment Overrides
- **Location**: `environments/<env-name>/overrides/`  
- **Purpose**: Environment-specific customizations
- **Precedence**: Overrides baseline configurations

### Local Customizations
- **Location**: `environments/<env-name>/local/`
- **Purpose**: Instance-specific modifications
- **Precedence**: Highest (overrides everything)

## Configuration Merge Process

1. Start with baseline configuration
2. Apply environment-specific overrides
3. Apply local customizations
4. Generate final deployment package

```
Baseline + Environment Overrides + Local = Final Configuration
```

## Environment Management Workflows

### 1. Creating New Environment

```bash
# Initialize new environment structure
./scripts/init-environment.sh <environment-name>

# Configure environment-specific settings
edit environments/<environment-name>/config/environment.conf

# Add environment-specific overrides
mkdir environments/<environment-name>/overrides/
# Add custom configurations...

# Validate configuration
./scripts/validate-config.sh <environment-name>

# Deploy to Splunk environment
./scripts/deploy.sh <environment-name>
```

### 2. Updating Baseline Template

```bash
# Make changes to baseline
edit environments/baseline/

# Test in development first
./scripts/deploy.sh development

# Validate changes
./scripts/validate-config.sh development

# Sync to other environments
./scripts/sync-baseline.sh staging
./scripts/sync-baseline.sh production
```

### 3. Environment-Specific Customizations

```bash
# Add override for specific environment
mkdir -p environments/production/overrides/dashboards/executive/
cp new_dashboard.xml environments/production/overrides/dashboards/executive/

# Validate override doesn't break configuration
./scripts/validate-config.sh production

# Deploy changes
./scripts/deploy.sh production
```

## Configuration Best Practices

### Baseline Design
- Keep baseline as generic as possible
- Use parameterized configurations
- Document all configurable options
- Maintain backward compatibility
- Test baseline changes thoroughly

### Environment Overrides
- Override only what's necessary
- Document reasons for overrides
- Use consistent naming conventions
- Validate override compatibility
- Keep overrides minimal and focused

### Version Control Strategy
- Use feature branches for baseline changes
- Tag stable baseline versions
- Track environment-specific changes separately
- Document deployment history
- Maintain rollback procedures

## Environment Types

### Development
**Purpose**: Testing and validation of new configurations
**Characteristics**:
- Shorter data retention
- More frequent updates
- Debug logging enabled
- Mock external integrations
- Relaxed security policies

### Staging  
**Purpose**: Pre-production validation and performance testing
**Characteristics**:
- Production-like configuration
- Full integration testing
- Load testing enabled
- Automated validation
- Regression testing

### Production
**Purpose**: Live operational environment
**Characteristics**:
- Extended data retention
- Strict security policies
- Full compliance enforcement
- High availability configuration
- Comprehensive monitoring

## Deployment Strategies

### Blue-Green Deployment
1. Prepare new configuration in "green" environment
2. Validate thoroughly in green
3. Switch traffic from "blue" to "green"
4. Keep blue as rollback option

### Rolling Deployment
1. Deploy to one instance/cluster member
2. Validate functionality
3. Gradually deploy to remaining instances
4. Monitor for issues at each step

### Canary Deployment  
1. Deploy to small subset of instances
2. Monitor performance and errors
3. Gradually increase deployment percentage
4. Full deployment once validated

## Monitoring and Validation

### Configuration Drift Detection
```bash
# Compare environment against baseline
./scripts/compare-environments.sh production baseline

# Generate drift report
./scripts/generate-drift-report.sh production
```

### Health Checks
- Configuration syntax validation
- Data model acceleration status
- Dashboard functionality tests  
- Knowledge object validation
- Performance metric checks

### Automated Validation
- Pre-deployment configuration checks
- Post-deployment functionality tests
- Performance regression detection
- Security policy validation
- Compliance requirement verification

## Troubleshooting

### Common Issues

**Configuration Conflicts**
- Check precedence order (baseline < override < local)
- Validate merge logic
- Review configuration syntax

**Deployment Failures**  
- Check Splunk logs for errors
- Validate file permissions
- Verify network connectivity
- Review deployment scripts

**Performance Issues**
- Monitor resource usage post-deployment
- Check data model acceleration
- Review search performance
- Validate index configurations

### Rollback Procedures

**Emergency Rollback**
```bash
# Rollback to previous configuration
./scripts/rollback.sh <environment-name> <previous-version>

# Validate rollback success
./scripts/validate-config.sh <environment-name>
```

**Selective Rollback**
```bash
# Rollback specific component
./scripts/rollback-component.sh <environment-name> dashboards <version>
```

## Integration with CI/CD

### GitOps Workflow
1. Configuration changes via pull requests
2. Automated validation on PR
3. Deployment triggered on merge
4. Post-deployment validation
5. Automatic rollback on failure

### Pipeline Stages
1. **Validate**: Syntax and policy checks
2. **Test**: Deploy to development environment
3. **Stage**: Deploy to staging for validation  
4. **Approve**: Manual approval for production
5. **Deploy**: Automated production deployment
6. **Monitor**: Post-deployment health checks

For detailed script usage and examples, see the individual script documentation in the `scripts/` directory.