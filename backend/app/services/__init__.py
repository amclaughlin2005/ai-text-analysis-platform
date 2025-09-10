"""
Service layer for the AI-Powered Text Analysis Platform
Provides business logic and data access layer
"""

from .dataset_service import DatasetService
from .analysis_service import AnalysisService

__all__ = [
    'DatasetService',
    'AnalysisService'
]
