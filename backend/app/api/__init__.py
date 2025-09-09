"""API endpoints for the AI-Powered Text Analysis Platform"""

# Import routers for main app registration
from . import datasets
from . import analysis
from . import wordcloud
from . import analytics
from . import export_router

__all__ = [
    'datasets',
    'analysis', 
    'wordcloud',
    'analytics',
    'export_router'
]
