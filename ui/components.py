"""
============================================
COGNIVAULT AI BUSINESS ANALYST AGENT
UI Components Module
============================================

Purpose:
    Reusable Streamlit UI components for consistent design across the application.

Components:
    - Custom chat messages
    - File upload widgets
    - Result cards
    - Loading animations
    - Metric displays

Author: Cognivault Team
Version: 1.0.0
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from pathlib import Path


def display_logo(logo_path: Optional[str] = None):
    """
    Display application logo/header using Streamlit native components.
    
    Args:
        logo_path (str, optional): Path to logo image. Shows title if None.
    """
    if logo_path and Path(logo_path).exists():
        # Display actual logo if file exists
        st.image(logo_path, width=600)
    else:
        # Display branded title using Streamlit components
        st.title("🧠 Cognivault AI")
        st.subheader("Business Analyst Agent") 
        st.markdown("Where intuition meets automation")
        st.markdown("---")  # Horizontal line separator


def chat_message(message: str, role: str = "assistant", avatar: Optional[str] = None):
    """
    Display a chat message with custom styling.
    
    Args:
        message (str): Message content.
        role (str): 'user' or 'assistant'.
        avatar (str, optional): Avatar emoji or image path.
    """
    # Default avatars
    if avatar is None:
        avatar = "👤" if role == "user" else "🤖"
    
    # Display message using Streamlit's chat_message
    with st.chat_message(role, avatar=avatar):
        st.markdown(message)


def file_upload_card(
    title: str,
    accepted_types: List[str],
    key: str,
    help_text: Optional[str] = None
) -> Optional[Any]:
    """
    Create a file upload widget.
    
    Args:
        title (str): Card title.
        accepted_types (List[str]): List of accepted file extensions.
        key (str): Unique key for the uploader.
        help_text (str, optional): Help text to display.
    
    Returns:
        Uploaded file object or None.
    """
    # Display title using Streamlit
    st.markdown(f"### 📁 {title}")
    
    # File uploader
    uploaded_file = st.file_uploader(
        label=title,
        type=accepted_types,
        key=key,
        help=help_text,
        label_visibility="collapsed"
    )
    
    return uploaded_file


def result_card(
    title: str,
    content: str,
    card_type: str = "info"
):
    """
    Display a result card using Streamlit native components.
    
    Args:
        title (str): Card title.
        content (str): Card content (supports markdown).
        card_type (str): 'info', 'success', 'warning', or 'error'.
    """
    # Icon mapping for different card types
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    icon = icons.get(card_type, 'ℹ️')
    
    # Display using native Streamlit components
    st.markdown(f"### {icon} {title}")
    st.markdown(content)
    st.markdown("---")


def metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊"
):
    """
    Display a metric card with icon.
    
    Args:
        label (str): Metric label.
        value (str): Metric value.
        delta (str, optional): Change indicator.
        icon (str): Icon emoji.
    """
    # Display metric with icon
    st.markdown(f"## {icon}")
    st.metric(label=label, value=value, delta=delta)


def loading_spinner(message: str = "Processing..."):
    """
    Display a loading spinner with custom message.
    
    Args:
        message (str): Loading message.
    
    Returns:
        Streamlit spinner context manager.
    """
    return st.spinner(message)


def citation_card(citations: List[Dict]):
    """
    Display citations from RAG responses.
    
    Args:
        citations (List[Dict]): List of citation dictionaries.
    """
    if not citations:
        return
    
    st.markdown("### 📚 Sources")
    
    for i, citation in enumerate(citations, 1):
        source = citation.get('source', 'Unknown')
        page_info = citation.get('page_info', 'Unknown')
        relevance = citation.get('relevance', 0.0)
        
        # Display citation using Streamlit
        st.markdown(f"**[{i}]** {source} - {page_info} (Relevance: {relevance:.2%})")


def analysis_type_selector() -> str:
    """
    Display business analysis type selector.
    
    Returns:
        str: Selected analysis type.
    """
    st.markdown("### 📋 Select Analysis Type")
    
    analysis_types = {
        "SWOT Analysis": "swot",
        "TOWS Matrix": "tows",
        "Porter's 5 Forces": "porter",
        "Competitor Analysis": "competitor",
        "Market Research": "market",
        "Pricing Strategy": "pricing",
        "GTM Strategy": "gtm"
    }
    
    selected = st.selectbox(
        "Choose analysis framework:",
        options=list(analysis_types.keys()),
        key="analysis_type_selector"
    )
    
    return analysis_types[selected]


def voice_player(audio_path: Optional[str] = None, audio_bytes: Optional[bytes] = None):
    """
    Display audio player for voice output.
    
    Args:
        audio_path (str, optional): Path to audio file.
        audio_bytes (bytes, optional): Audio data as bytes.
    """
    st.markdown("### 🔊 Voice Output")
    
    if audio_path:
        st.audio(audio_path)
    elif audio_bytes:
        st.audio(audio_bytes)
    else:
        st.info("No audio available")


def data_preview_table(df, max_rows: int = 10):
    """
    Display data preview table with styling.
    
    Args:
        df: Pandas DataFrame.
        max_rows (int): Maximum rows to display.
    """
    st.markdown("### 📊 Data Preview")
    st.dataframe(df.head(max_rows), use_container_width=True)
    
    # Show data info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


def visualization_gallery(viz_paths: Dict[str, str]):
    """
    Display gallery of visualizations.
    
    Args:
        viz_paths (Dict[str, str]): Dictionary of visualization names and paths.
    """
    if not viz_paths:
        return
    
    st.markdown("### 📈 Visualizations")
    
    # Display visualizations in a grid
    cols = st.columns(2)
    
    for i, (name, path) in enumerate(viz_paths.items()):
        with cols[i % 2]:
            st.markdown(f"**{name.replace('_', ' ').title()}**")
            if Path(path).exists():
                st.image(path, use_container_width=True)
            else:
                st.warning(f"Visualization not found: {path}")


def sidebar_info():
    """
    Display sidebar information and settings.
    """
    with st.sidebar:
        st.markdown("## Live Info")
        
        # Mode indicator
        if 'current_mode' in st.session_state:
            st.info(f"**Current Mode:** {st.session_state.current_mode}")
        
        # Session stats
        st.markdown("### 📊 Session Stats")
        
        docs_count = st.session_state.get('documents_count', 0)
        datasets_count = st.session_state.get('datasets_count', 0)
        
        st.metric("Documents Uploaded", docs_count)
        st.metric("Datasets Loaded", datasets_count)
        
        # About section
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
At Cognivault AI, I believe business intelligence should be easy. My platform gives you a smooth, AI-powered workspace that turns raw data and documents into clear insights and saves your time.

**My Offerings:**
- Smart Business Consulting
- Robust RAG-based Document Q&A
- Intelligent Data Analysis
        """)
        
        st.markdown("---")
        st.markdown("**Created by Parth B Mistry**")


def custom_css():
    
    st.title("UI Components Test")
    
    # Test chat message
    chat_message("Hello! This is a test message.", "assistant")
    chat_message("This is a user message.", "user")
    
    # Test result card
    result_card("Success", "This is a success message!", "success")
    
    # Test metric card
    metric_card("Total Users", "1,234", "+12%", "👥")
    
    st.success("UI Components loaded successfully!")
