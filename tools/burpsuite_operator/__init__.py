"""
BurpSuite Operator tools for cybersecurity AI workflow integration.

This module provides tools for integrating with and controlling BurpSuite Professional,
including scan orchestration, result processing, and vulnerability assessment.
"""

from .BurpSuiteAPIClient import BurpSuiteAPIClient
from .BurpScanOrchestrator import BurpScanOrchestrator
from .BurpResultProcessor import BurpResultProcessor
from .BurpVulnerabilityAssessor import BurpVulnerabilityAssessor

__all__ = [
    "BurpSuiteAPIClient",
    "BurpScanOrchestrator", 
    "BurpResultProcessor",
    "BurpVulnerabilityAssessor",
]
