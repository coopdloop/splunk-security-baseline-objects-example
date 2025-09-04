# Splunk Technical Add-on Repository Template

A comprehensive repository template for security engineers to organize, track, and manage Splunk Technical Add-ons (TAs), focusing on data model work, knowledge objects, and security dashboards.

## 🚀 Dashboard Generation System

**NEW**: This repository now includes a powerful dashboard generation CLI that creates parameterized Splunk dashboards for multiple environments.

### Quick Dashboard Generation
```bash
# Setup
uv sync

# List available templates  
uv run create-dashboard list-templates

# Generate a dashboard
uv run create-dashboard generate simple_data_validation \
  --environment production \
  --config-file config.json
```

## Repository Structure

```
├── src/                      # Python dashboard generation system
│   └── splunk_ta_repo/      # Dashboard CLI and template engine
├── templates/               # Parameterized JSON dashboard templates
│   └── dashboard-templates/ # Template library (JSON)
├── environments/            # Multi-environment management
│   ├── baseline/           # Core template inherited by all environments
│   │   ├── data-models/    # Standard CIM data models
│   │   ├── knowledge-objects/ # Common knowledge objects  
│   │   ├── dashboards/     # Standard dashboards
│   │   └── config/         # Base configuration
│   ├── development/        # Development environment overrides
│   ├── staging/           # Staging environment overrides  
│   └── production/        # Production environment overrides
├── environment-management/  # Environment management tools
│   ├── scripts/           # Deployment and sync scripts
│   ├── configs/          # Management configurations
│   └── templates/        # Environment templates
├── docs/                 # Documentation and guides  
└── examples/            # Sample implementations
```

## ✨ Key Features

### 🎯 Dashboard Generation System
- **Parameterized Templates** - Create dashboards with configurable parameters
- **Multi-Environment Support** - Generate environment-specific dashboards
- **Interactive CLI** - Rich terminal interface with prompts and validation
- **Config File Support** - Reusable parameter configurations
- **Template Validation** - Automatic JSON syntax and structure validation
- **Metadata Tracking** - Version control and change tracking
- **🆕 Handlebars Support** - Advanced templating with .json.hbs files
- **🆕 Strict Validation Mode** - Performance and security checking
- **🆕 Enhanced Template Engine** - Comprehensive error detection and validation

### 🏗️ Multi-Environment Management
This repository supports managing Splunk configurations across multiple environments with inheritance:

**Baseline Template**
- Core configurations shared across all environments
- CIM-compliant data models and standard knowledge objects
- Common dashboards and saved searches
- Located in `environments/baseline/`

**Environment-Specific Overrides**
- **Development**: Testing configurations with shorter retention
- **Staging**: Production-like settings for validation  
- **Production**: Full compliance and extended retention
- Each environment inherits from baseline and adds customizations

**Management Tools**
- **Environment initialization**: `./environment-management/scripts/init-environment.sh`
- **Baseline synchronization**: `./environment-management/scripts/sync-baseline.sh`
- **Deployment automation**: `./environment-management/scripts/deploy.sh`

## Quick Start

### 📊 Dashboard Generation (Recommended)
1. **Setup**: `uv sync` - Install dependencies
2. **Quick Start Guide**: See [QUICKSTART.md](QUICKSTART.md)
3. **Working Example**: See [WORKING_EXAMPLE.md](WORKING_EXAMPLE.md)
4. **Generate Dashboard**:
   ```bash
   # Basic JSON template
   uv run create-dashboard generate simple_data_validation \
     --environment production
   
   # NEW: Advanced Handlebars template
   uv run create-dashboard generate security_basic \
     --environment production --config-file security_config.json
   
   # NEW: Strict validation
   uv run create-dashboard validate-template security_basic --strict
   ```

### 🔧 Traditional Setup
1. **Contributing Data Models**: See [docs/contributing-data-models.md](docs/contributing-data-models.md)
2. **Contributing Knowledge Objects**: See [docs/contributing-knowledge-objects.md](docs/contributing-knowledge-objects.md)
3. **Contributing Dashboards**: See [docs/contributing-dashboards.md](docs/contributing-dashboards.md)

### 🏗️ Multi-Environment Setup
1. **Environment Management**: See [environments/README.md](environments/README.md)
2. **Initialize new environment**: `./environment-management/scripts/init-environment.sh <env-name>`
3. **Deploy to environment**: `./environment-management/scripts/deploy.sh <env-name>`

## 🚀 Deployment Support

This repository supports both:
- **Splunk Cloud** - See [docs/cloud-deployment.md](docs/cloud-deployment.md)
- **On-Premises** - See [docs/on-premises-deployment.md](docs/on-premises-deployment.md)
- **Dashboard Studio** - Generated dashboards import directly into Splunk Dashboard Studio

## 🔗 Integration Examples

- External threat intelligence feeds
- Security orchestration platforms
- Vulnerability scanners
- Network security tools
- CI/CD pipeline integration for automated dashboard deployment

## 📚 Available Dashboard Templates

| Template | Category | Format | Description |
|----------|----------|--------|-------------|
| `simple_data_validation` | validation | .json | Basic data source validation and monitoring |
| `data_source_validation` | validation | .json | Comprehensive data source monitoring with ingestion tracking |
| `cim_compliance` | compliance | .json | CIM field population and data model compliance validation |
| `streams_monitoring` | monitoring | .json | Splunk Streams performance and network traffic analysis |
| `security_basic` | security | **.json.hbs** | **NEW** - Advanced security monitoring with Handlebars templating |

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/splunk-ta-repo.git
   cd splunk-ta-repo
   ```

2. **Setup dashboard generation (recommended)**
   ```bash
   uv sync
   uv run create-dashboard list-templates
   ```

3. **Traditional approach - choose your focus area**:
   - **Data Models**: Start with [data-models/README.md](data-models/README.md)
   - **Knowledge Objects**: Start with [knowledge-objects/README.md](knowledge-objects/README.md)
   - **Dashboards**: Start with [dashboards/README.md](dashboards/README.md)

4. **Review examples**: Check the [examples/](examples/) directory for sample implementations

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- How to submit changes
- Quality standards
- Review process
- Community guidelines

## License

## 🛠️ Dependencies

- **Python 3.8+** with uv package manager
- **Rich** for beautiful terminal output
- **Click** for CLI framework
- **Jinja2** for template rendering

## 📈 System Status

✅ **Dashboard Generation** - Fully operational with 4 validated templates  
✅ **Template Validation** - JSON syntax validation implemented  
✅ **Multi-Environment** - Production-ready environment management  
✅ **CLI Interface** - Rich interactive and config file modes  
✅ **Documentation** - Comprehensive guides and working examples  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.