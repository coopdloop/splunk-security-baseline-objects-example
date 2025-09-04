"""Custom exceptions for the splunk-ta-repo package."""


class SplunkTARepoError(Exception):
    """Base exception for all splunk-ta-repo errors."""
    pass


class TemplateError(SplunkTARepoError):
    """Raised when there's an error with template processing."""
    pass


class ValidationError(SplunkTARepoError):
    """Raised when validation fails."""
    pass


class EnvironmentError(SplunkTARepoError):
    """Raised when there's an environment management error."""
    pass