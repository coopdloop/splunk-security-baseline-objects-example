"""Splunk Technical Add-on Repository Template

A comprehensive system for managing Splunk TAs across multiple environments
with parameterized dashboard generation.
"""

__version__ = "1.0.0"
__author__ = "Security Engineering Team"

from .dashboard_generator import DashboardGenerator
from .template_engine import render_template

__all__ = ["DashboardGenerator", "render_template"]