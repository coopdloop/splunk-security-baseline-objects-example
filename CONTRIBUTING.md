# Contributing to Splunk TA Repository

Thank you for your interest in contributing to this Splunk Technical Add-on repository template! This guide will help you get started.

## How to Contribute

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/splunk-ta-repo.git
cd splunk-ta-repo
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
Follow the specific contribution guides for each content type:
- [Data Models](docs/contributing-data-models.md)
- [Knowledge Objects](docs/contributing-knowledge-objects.md)  
- [Dashboards](docs/contributing-dashboards.md)

### 4. Test Your Changes
- Validate configurations in a Splunk environment
- Test field extractions with sample data
- Verify dashboard functionality
- Check CIM compliance where applicable

### 5. Document Your Work
- Update relevant README files
- Include sample data or queries
- Document any new dependencies
- Fill out the metadata template if adding new TAs

### 6. Submit a Pull Request
- Use clear, descriptive commit messages
- Reference any related issues
- Include screenshots for dashboards
- Provide testing instructions

## Content Guidelines

### Data Models
- Must be CIM-compliant where possible
- Include comprehensive field mapping documentation
- Provide sample events and extractions
- Document performance considerations

### Knowledge Objects
- Use standard naming conventions
- Test all regular expressions thoroughly
- Include performance impact assessment
- Document any external dependencies

### Dashboards
- Follow consistent visual design
- Include appropriate drill-down actions
- Optimize for performance
- Provide mobile-friendly layouts where possible

### External Integrations
- Include comprehensive error handling
- Document API requirements and limitations
- Provide configuration examples
- Include security best practices

## Quality Standards

### Code Quality
- Follow PEP 8 for Python code
- Use meaningful variable names
- Include appropriate comments
- Handle errors gracefully

### Documentation Quality
- Use clear, concise language
- Include practical examples
- Provide troubleshooting guidance
- Keep documentation up-to-date

### Security Requirements
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Follow principle of least privilege
- Document security implications

## Review Process

### Automated Checks
- Configuration syntax validation
- Documentation completeness check
- Security scanning for sensitive data

### Manual Review
- Code quality assessment
- Documentation review
- Functionality testing
- Security review

## Community Guidelines

### Be Respectful
- Use inclusive language
- Respect different perspectives
- Be constructive in feedback
- Help newcomers learn

### Be Collaborative
- Share knowledge openly
- Provide helpful feedback
- Acknowledge contributions
- Work together to solve problems

## Getting Help

### Questions?
- Open a discussion in the repository
- Tag relevant maintainers
- Check existing documentation first
- Be specific about your environment

### Reporting Issues
- Use the issue templates
- Provide detailed reproduction steps
- Include environment information
- Attach relevant logs or screenshots

### Feature Requests
- Explain the use case clearly
- Describe the expected behavior
- Consider implementation complexity
- Be open to alternative solutions

## Recognition

Contributors are recognized through:
- Credits in documentation
- Contributor listings
- Community acknowledgments
- Maintainer opportunities for consistent contributors

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.

## Quick Reference

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes  
- `docs/description` - Documentation updates
- `refactor/description` - Code improvements

### Commit Messages
```
type(scope): description

Examples:
feat(dashboard): add network anomaly detection dashboard
fix(props): correct field extraction for palo alto logs  
docs(readme): update installation instructions
```

### File Structure
- Keep similar content together
- Use descriptive file names
- Follow established naming conventions
- Include README files in new directories

Thank you for contributing to making Splunk security knowledge more accessible and organized!