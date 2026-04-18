"""
============================================
COGNIVAULT AI BUSINESS ANALYST AGENT
UI Package Initialization
============================================

This package contains all UI components for the Streamlit application.
"""

__version__ = "1.0.0"
__author__ = "Cognivault Team"

from ui.components import (
    display_logo,
    chat_message,
    file_upload_card,
    result_card,
    metric_card,
    citation_card,
    analysis_type_selector,
    voice_player,
    data_preview_table,
    visualization_gallery,
    sidebar_info,
    custom_css
)

__all__ = [
    "display_logo",
    "chat_message",
    "file_upload_card",
    "result_card",
    "metric_card",
    "citation_card",
    "analysis_type_selector",
    "voice_player",
    "data_preview_table",
    "visualization_gallery",
    "sidebar_info",
    "custom_css"
]
