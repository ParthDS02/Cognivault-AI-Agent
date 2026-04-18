"""
============================================
COGNIVAULT AI BUSINESS ANALYST AGENT
Main Streamlit Application
============================================

Purpose:
    Main web application interface for Cognivault AI Business Analyst Agent.
    Provides 4-mode unified interface for business consulting, RAG, data analysis, and voice.

Features:
    - Business Consulting Mode
    - RAG Document Q&A Mode
    - Data Analysis & AutoML Mode
    - Voice Generation Mode
    - Session state management
    - File upload handling
    - Interactive chat interface

Author: Cognivault Team
Version: 1.0.0

Usage:
    streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import traceback

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Import backend modules
from backend.config import Config
from backend.router import CognivaultRouter, AgentMode
from backend.elevenlabs_client import VoicePresets
from backend.report_generator import PDFReportGenerator, PPTReportGenerator

# Import UI components
from ui.components import (
    display_logo, chat_message, file_upload_card, result_card,
    metric_card, citation_card, analysis_type_selector, voice_player,
    data_preview_table, visualization_gallery, sidebar_info
)


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Cognivault AI Business Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def initialize_session_state():
    """
    Initialize Streamlit session state variables.
    """
    # Initialize router (singleton pattern)
    if 'router' not in st.session_state:
        try:
            st.session_state.router = CognivaultRouter()
            st.session_state.router_initialized = True
        except Exception as e:
            st.session_state.router_initialized = False
            st.session_state.router_error = str(e)
    
    # Initialize chat histories for each mode
    if 'chat_history_consulting' not in st.session_state:
        st.session_state.chat_history_consulting = []
    
    if 'chat_history_rag' not in st.session_state:
        st.session_state.chat_history_rag = []
    
    if 'chat_history_data' not in st.session_state:
        st.session_state.chat_history_data = []
    
    # Initialize counters
    if 'documents_count' not in st.session_state:
        st.session_state.documents_count = 0
    
    if 'datasets_count' not in st.session_state:
        st.session_state.datasets_count = 0
    
    # Current mode
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "Business Consulting"
    
    # Analysis results storage
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    
    if 'current_visualizations' not in st.session_state:
        st.session_state.current_visualizations = {}


# ============================================
# HELPER FUNCTIONS
# ============================================

def save_uploaded_file(uploaded_file, destination_folder: str) -> str:
    """
    Save uploaded file to destination folder.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        destination_folder (str): Destination folder path.
    
    Returns:
        str: Path to saved file.
    """
    dest_path = Path(destination_folder)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    file_path = dest_path / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(file_path)


def add_message_to_history(history_key: str, role: str, content: str):
    """
    Add message to chat history.
    
    Args:
        history_key (str): Session state key for history.
        role (str): 'user' or 'assistant'.
        content (str): Message content.
    """
    if history_key in st.session_state:
        st.session_state[history_key].append({
            'role': role,
            'content': content
        })


# ============================================
# MODE 1: BUSINESS CONSULTING
# ============================================

def business_consulting_mode():
    """
    Business Consulting Mode UI and logic.
    """
    st.header("🎯 Business Consulting & Strategy")
    st.markdown("Get expert business analysis using proven frameworks like SWOT, Porter's 5 Forces, and more.")
    
    # Analysis type selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = analysis_type_selector()
    
    with col2:
        st.markdown("### 🔊 Voice Output")
        enable_voice = st.checkbox("Enable voice narration", value=False, key="consulting_voice")
    
    # Input section
    st.markdown("### 💬 Your Question")
    
    # Provide example prompts based on analysis type
    examples = {
        'swot': "Perform SWOT analysis for Tesla in the electric vehicle market",
        'tows': "Create TOWS matrix for Apple's iPhone business",
        'porter': "Analyze the smartphone industry using Porter's 5 Forces",
        'competitor': "Compare Netflix vs Disney+ vs Amazon Prime Video",
        'market': "Research the AI chatbot market size and trends",
        'pricing': "Develop pricing strategy for a SaaS project management tool",
        'gtm': "Create go-to-market plan for a new fitness app",
        'general': "How can I improve customer retention for my e-commerce business?"
    }
    
    example = examples.get(analysis_type, "")
    
    user_input = st.text_area(
        "Enter your business question:",
        placeholder=f"Example: {example}",
        height=100,
        key="consulting_input"
    )
    
    # Additional context (optional)
    with st.expander("➕ Add Additional Context (Optional)"):
        company = st.text_input("Company/Product Name:", key="consulting_company")
        industry = st.text_input("Industry:", key="consulting_industry")
        additional_info = st.text_area("Additional Information:", key="consulting_additional")
    
    # Submit button
    if st.button("🚀 Generate Analysis", key="consulting_submit", type="primary"):
        if user_input.strip():
            with st.spinner("🔄 Analyzing... This may take a moment..."):
                try:
                    # Build context
                    context = {
                        'company': company if company else None,
                        'industry': industry if industry else None,
                        'additional_context': additional_info if additional_info else None,
                        'analysis_type': analysis_type
                    }
                    
                    # Route request
                    response = st.session_state.router.route_request(
                        user_input,
                        mode=AgentMode.BUSINESS_CONSULTING,
                        context=context
                    )
                    
                    if response['success']:
                        result = response['result']
                        
                        # Display result
                        result_card("Analysis Complete", result['response'], "success")
                        
                        # Add to chat history
                        add_message_to_history('chat_history_consulting', 'user', user_input)
                        add_message_to_history('chat_history_consulting', 'assistant', result['response'])
                        
                        # Voice generation if enabled
                        if enable_voice and result.get('can_generate_voice'):
                            with st.spinner("🔊 Generating voice narration..."):
                                try:
                                    voice_result = st.session_state.router.route_request(
                                        result['response'][:1000],  # Limit length for voice
                                        mode=AgentMode.VOICE_GENERATION
                                    )
                                    
                                    if voice_result['success']:
                                        voice_player(audio_bytes=voice_result['result'].get('audio_bytes'))
                                except Exception as e:
                                    st.warning(f"Voice generation failed: {str(e)}")
                        
                        
                        # Export Reports
                        st.markdown("---")
                        st.markdown("### 📥 Download Professional Reports")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Generate PDF
                            try:
                                pdf_gen = PDFReportGenerator()
                                pdf_bytes = pdf_gen.generate_consulting_report(analysis_type, result['response'])
                                
                                st.download_button(
                                    label="📄 Download PDF Report",
                                    data=pdf_bytes,
                                    file_name=f"cognivault_report_{analysis_type.lower().replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"PDF generation failed: {str(e)}")
                        
                        with col2:
                            # Generate PowerPoint
                            try:
                                ppt_gen = PPTReportGenerator()
                                ppt_bytes = ppt_gen.generate_consulting_presentation(analysis_type, result['response'])
                                
                                st.download_button(
                                    label="📊 Download PowerPoint",
                                    data=ppt_bytes,
                                    file_name=f"cognivault_presentation_{analysis_type.lower().replace(' ', '_')}.pptx",
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"PPT generation failed: {str(e)}")
                    
                    else:
                        st.error(f"Analysis failed: {response.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    if Config.DEBUG_MODE:
                        st.code(traceback.format_exc())
        else:
            st.warning("Please enter a question or request.")
    
    # Display chat history
    if st.session_state.chat_history_consulting:
        st.markdown("---")
        with st.expander("📜 Conversation History", expanded=False):
            for msg in st.session_state.chat_history_consulting[-6:]:  # Show last 6 messages
                chat_message(msg['content'], msg['role'])


# ============================================
# MODE 2: RAG DOCUMENT Q&A
# ============================================

def rag_documents_mode():
    """
    RAG Document Q&A Mode UI and logic.
    """
    st.header("📄 Document Q&A (RAG)")
    st.markdown("Upload documents and ask questions. Get answers with citations.")
    
    # File upload section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_doc = file_upload_card(
            title="Upload Document",
            accepted_types=['pdf', 'docx', 'pptx'],
            key="rag_file_upload",
            help_text="Upload PDF, DOCX, or PPTX files"
        )
        
        if uploaded_doc:
            if st.button("📥 Process Document", key="rag_process"):
                with st.spinner("🔄 Processing document..."):
                    try:
                        # Save file
                        file_path = save_uploaded_file(uploaded_doc, Config.DOCUMENTS_UPLOAD_PATH)
                        
                        # Add to RAG engine
                        result = st.session_state.router.add_document(file_path)
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.session_state.documents_count += 1
                        else:
                            st.error(f"❌ {result['error']}")
                    
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
    
    with col2:
        st.markdown("### 📊 Document Stats")
        metric_card("Documents Loaded", str(st.session_state.documents_count), icon="📚")
    
    # Q&A Section
    st.markdown("---")
    st.markdown("### 💬 Ask Questions About Your Documents")
    
    user_question = st.text_input(
        "Your question:",
        placeholder="Example: What is the revenue breakdown by segment?",
        key="rag_question"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ask_button = st.button("🔍 Get Answer", key="rag_ask", type="primary")
    
    with col2:
        enable_voice = st.checkbox("Voice", value=False, key="rag_voice")
    
    if ask_button:
        if user_question.strip():
            if st.session_state.documents_count == 0:
                st.warning("⚠️ Please upload at least one document first.")
            else:
                with st.spinner("🔄 Searching documents..."):
                    try:
                        response = st.session_state.router.route_request(
                            user_question,
                            mode=AgentMode.RAG_DOCUMENTS
                        )
                        
                        if response['success']:
                            result = response['result']
                            
                            # Display answer
                            result_card("Answer", result['response'], "info")
                            
                            # Display citations
                            if result.get('citations'):
                                citation_card(result['citations'])
                            
                            # Add to history
                            add_message_to_history('chat_history_rag', 'user', user_question)
                            add_message_to_history('chat_history_rag', 'assistant', result['response'])
                            
                            # Voice if enabled
                            if enable_voice:
                                with st.spinner("🔊 Generating voice..."):
                                    try:
                                        voice_result = st.session_state.router.route_request(
                                            result['response'][:1000],
                                            mode=AgentMode.VOICE_GENERATION
                                        )
                                        if voice_result['success']:
                                            voice_player(audio_bytes=voice_result['result'].get('audio_bytes'))
                                    except:
                                        pass
                            
                            
                            # Export Reports
                            st.markdown("---")
                            st.markdown("### 📥 Download Professional Reports")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Generate PDF
                                try:
                                    pdf_gen = PDFReportGenerator()
                                    pdf_bytes = pdf_gen.generate_rag_report(user_question, result['response'])
                                    
                                    st.download_button(
                                        label="📄 Download PDF Answer",
                                        data=pdf_bytes,
                                        file_name="cognivault_rag_answer.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error(f"PDF generation failed: {str(e)}")
                            
                            with col2:
                                # Generate PowerPoint
                                try:
                                    ppt_gen = PPTReportGenerator()
                                    ppt_bytes = ppt_gen.generate_rag_presentation(user_question, result['response'])
                                    
                                    st.download_button(
                                        label="📊 Download PowerPoint",
                                        data=ppt_bytes,
                                        file_name="cognivault_rag_answer.pptx",
                                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error(f"PPT generation failed: {str(e)}")
                        
                        else:
                            st.error(f"Error: {response.get('error')}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question.")
    
    # Chat history
    if st.session_state.chat_history_rag:
        st.markdown("---")
        with st.expander("📜 Recent Questions", expanded=False):
            for msg in st.session_state.chat_history_rag[-4:]:
                chat_message(msg['content'], msg['role'])


# ============================================
# MODE 3: DATA ANALYSIS & AUTOML
# ============================================

def data_analysis_mode():
    """
    Data Analysis & AutoML Mode UI and logic.
    """
    st.header("📊 Data Analysis & AutoML")
    st.markdown("Upload datasets for automated EDA, visualization, and machine learning.")
    
    # File upload
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_data = file_upload_card(
            title="Upload Dataset",
            accepted_types=['csv', 'xlsx', 'xls'],
            key="data_file_upload",
            help_text="Upload CSV or Excel files"
        )
        
        if uploaded_data:
            if st.button("📥 Load Dataset", key="data_load"):
                with st.spinner("🔄 Loading dataset..."):
                    try:
                        # Save file
                        file_path = save_uploaded_file(uploaded_data, Config.DATASETS_UPLOAD_PATH)
                        
                        # Load dataset
                        result = st.session_state.router.load_dataset(file_path)
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.session_state.datasets_count += 1
                            
                            # Display preview
                            data_preview_table(st.session_state.router.data_analyzer.df)
                        else:
                            st.error(f"❌ {result['error']}")
                    
                    except Exception as e:
                        st.error(f"Error loading dataset: {str(e)}")
    
    with col2:
        st.markdown("### 📈 Dataset Stats")
        metric_card("Datasets Loaded", str(st.session_state.datasets_count), icon="📊")
    
    # Analysis options
    if st.session_state.router.data_analyzer.df is not None:
        st.markdown("---")
        st.markdown("### 🔬 Analysis Options")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Schema", "🔍 Null Values", "📊 EDA", "📈 Visualizations", "🔍 Outlier Analysis"])
        
        with tab1:
            st.markdown("#### Data Schema & Structure")
            
            if st.button("🔍 Analyze Schema", key="analyze_schema"):
                with st.spinner("🔄 Detecting schema..."):
                    try:
                        schema = st.session_state.router.data_analyzer.detect_schema()
                        
                        st.success("✅ Schema Analysis Complete!")
                        
                        # Display summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            metric_card("Total Rows", str(schema['total_rows']), icon="📊")
                        with col2:
                            metric_card("Total Columns", str(schema['total_columns']), icon="📋")
                        with col3:
                            metric_card("Numeric Columns", str(len(schema['numeric_columns'])), icon="🔢")
                        
                        # Display column details
                        st.markdown("##### 📋 Column Information")
                        schema_df = []
                        for col, info in schema['columns'].items():
                            schema_df.append({
                                'Column': col,
                                'Type': info['dtype'],
                                'Nulls': info['null_count'],
                                'Null %': f"{info['null_percentage']:.1f}%",
                                'Unique': info['unique_count']
                            })
                        st.dataframe(schema_df, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with tab2:
            st.markdown("#### Null Values Analysis & Handling")
            
            if st.button("🔍 Analyze Null Values", key="analyze_nulls"):
                with st.spinner("🔄 Analyzing null values..."):
                    try:
                        null_analysis = st.session_state.router.data_analyzer.analyze_null_values()
                        
                        # Store in session state to persist across reruns
                        st.session_state.null_analysis = null_analysis
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Display analysis if available in session state
            if 'null_analysis' in st.session_state and st.session_state.null_analysis:
                null_analysis = st.session_state.null_analysis
                summary = null_analysis['summary']
                column_analysis = null_analysis['column_analysis']
                recommendations = null_analysis['recommendations']
                code_snippets = null_analysis['code_snippets']
                
                # Summary metrics
                st.markdown("##### 📊 Null Values Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    metric_card(
                        "Total Null Values", 
                        str(summary['total_nulls']),
                        delta=f"{summary['null_percentage']:.2f}% of data",
                        icon="❌"
                    )
                with col2:
                    metric_card(
                        "Columns with Nulls",
                        f"{summary['columns_with_nulls_count']}/{summary['total_columns']}",
                        icon="📋"
                    )
                with col3:
                    status = "🟢 Excellent" if summary['null_percentage'] < 5 else "🟡 Moderate" if summary['null_percentage'] < 20 else "🔴 High"
                    metric_card("Data Quality", status, icon="✨")
                
                # Column-wise analysis
                if column_analysis:
                    st.markdown("---")
                    st.markdown("##### 📊 Column-wise Null Distribution")
                    
                    # Create bar chart
                    import pandas as pd
                    null_df = pd.DataFrame(column_analysis)
                    
                    # Show table
                    st.dataframe(
                        null_df[['column', 'null_count', 'null_percentage', 'dtype']],
                       use_container_width=True,
                        column_config={
                            "column": "Column Name",
                            "null_count": "Null Count",
                            "null_percentage": st.column_config.NumberColumn(
                                "Null %",
                                format="%.2f%%"
                            ),
                            "dtype": "Data Type"
                        }
                    )
                    
                    # Smart Recommendations
                    st.markdown("---")
                    st.markdown("##### 💡 Smart Recommendations")
                    
                    for rec in recommendations:
                        with st.expander(f"**{rec['column']}** - {rec['recommended_strategy']} ({rec['null_percentage']:.1f}% nulls)"):
                            st.info(f"**Reason:** {rec['reason']}")
                            st.code(rec['example_code'], language='python')
                    
                    # Interactive Cleaning Actions
                    st.markdown("---")
                    st.markdown("##### ⚙️ Apply Cleaning Actions")
                    st.markdown("**Choose how to handle null values:**")
                    
                    # Column selector
                    cols_with_nulls = [item['column'] for item in column_analysis]
                    selected_column = st.selectbox(
                        "Select column to clean:",
                        options=["All Columns"] + cols_with_nulls,
                        key="null_column_selector"
                    )
                    
                   # Strategy selector
                    cleaning_strategy = st.selectbox(
                        "Select cleaning strategy:",
                        options=[
                            "Drop rows with nulls",
                            "Drop this column",
                            "Fill with median (numeric)",
                            "Fill with mean (numeric)",
                            "Fill with mode (most common)",
                            "Fill with constant value",
                            "Forward fill (use previous value)",
                            "Backward fill (use next value)"
                        ],
                        key="cleaning_strategy"
                    )
                    
                    # Constant value input (shown only for constant fill strategy)
                    if "constant" in cleaning_strategy.lower():
                        constant_value = st.text_input(
                            "Enter constant value to fill:",
                            key="constant_value"
                        )
                    
                    # Apply button
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        if st.button("🚀 Apply Cleaning", key="apply_cleaning_button", type="primary"):
                            try:
                                df = st.session_state.router.data_analyzer.df
                                
                                if selected_column == "All Columns":
                                    target_cols = cols_with_nulls
                                else:
                                    target_cols = [selected_column]
                                
                                # Apply the selected strategy
                                if "drop rows" in cleaning_strategy.lower():
                                    if selected_column == "All Columns":
                                        df = df.dropna()
                                        st.success(f"✅ Dropped all rows with any null values")
                                    else:
                                        df = df.dropna(subset=target_cols)
                                        st.success(f"✅ Dropped rows where '{selected_column}' has nulls")
                                
                                elif "drop this column" in cleaning_strategy.lower():
                                    if selected_column != "All Columns":
                                        df = df.drop(columns=target_cols)
                                        st.success(f"✅ Dropped column '{selected_column}'")
                                    else:
                                        st.warning("Cannot drop 'All Columns'. Please select a specific column.")
                                
                                elif "median" in cleaning_strategy.lower():
                                    for col in target_cols:
                                        if df[col].dtype in ['float64', 'int64']:
                                            df[col] = df[col].fillna(df[col].median())
                                            st.success(f"✅ Filled '{col}' with median value")
                                        else:
                                            st.warning(f"⚠️ '{col}' is not numeric, skipped")
                                
                                elif "mean" in cleaning_strategy.lower():
                                    for col in target_cols:
                                        if df[col].dtype in ['float64', 'int64']:
                                            df[col] = df[col].fillna(df[col].mean())
                                            st.success(f"✅ Filled '{col}' with mean value")
                                        else:
                                            st.warning(f"⚠️ '{col}' is not numeric, skipped")
                                
                                elif "mode" in cleaning_strategy.lower():
                                    for col in target_cols:
                                        mode_val = df[col].mode()
                                        if not mode_val.empty:
                                            df[col] = df[col].fillna(mode_val[0])
                                            st.success(f"✅ Filled '{col}' with mode (most common) value")
                                
                                elif "constant" in cleaning_strategy.lower():
                                    if 'constant_value' in locals():
                                        for col in target_cols:
                                            df[col] = df[col].fillna(constant_value)
                                            st.success(f"✅ Filled '{col}' with constant '{constant_value}'")
                                
                                elif "forward" in cleaning_strategy.lower():
                                    for col in target_cols:
                                        df[col] = df[col].ffill()
                                        st.success(f"✅ Forward filled '{col}'")
                                
                                elif "backward" in cleaning_strategy.lower():
                                    for col in target_cols:
                                        df[col] = df[col].bfill()
                                        st.success(f"✅ Backward filled '{col}'")
                                
                                # Update the dataframe
                                st.session_state.router.data_analyzer.df = df
                                # Clear the null analysis so user can re-analyze
                                st.session_state.null_analysis = None
                                st.success("✅ Cleaning applied! Click 'Analyze Null Values' again to see updated statistics")
                                
                            except Exception as e:
                                st.error(f"Error applying cleaning: {str(e)}")
                    
                    with col_b:
                        st.caption("⚠️ This will modify your dataset. You can reload to revert changes.")
                    
                    # Code Snippets
                    st.markdown("---")
                    st.markdown("##### 📝 Code Snippets for Handling Null Values")
                    st.markdown("Copy and use these code snippets in your data cleaning pipeline:")
                    
                    with st.expander("🗑️ Drop Strategies"):
                        st.code(code_snippets['drop_rows'], language='python')
                        st.code(code_snippets['drop_columns'], language='python')
                    
                    with st.expander("🔢 Fill Numeric Columns"):
                        st.code(code_snippets['fill_numeric_simple'], language='python')
                    
                    with st.expander("📝 Fill Categorical Columns"):
                        st.code(code_snippets['fill_categorical'], language='python')
                    
                    with st.expander("⚡ Advanced Filling Methods"):
                        st.code(code_snippets['fill_advanced'], language='python')
                    
                    with st.expander("🤖 Scikit-learn Imputation"):
                        st.code(code_snippets['sklearn_imputation'], language='python')
                
                else:
                    st.success("🎉 No null values found in your dataset!")
                    
            else:
                st.info("👆 Click 'Analyze Null Values' button above to start analysis")
        
        with tab3:
            st.markdown("#### Exploratory Data Analysis")
            
            if st.button("🚀 Run EDA", key="run_eda"):
                with st.spinner("🔄 Performing EDA..."):
                    try:
                        eda_results = st.session_state.router.data_analyzer.perform_eda()
                        
                        st.success("✅ EDA Complete!")
                        
                        # Display basic stats
                        st.markdown("##### 📊 Statistical Summary")
                        st.dataframe(st.session_state.router.data_analyzer.df.describe())
                        
                        # Display correlations if available
                        if 'strong_correlations' in eda_results:
                            st.markdown("##### 🔗 Strong Correlations")
                            for corr in eda_results['strong_correlations']:
                                st.write(f"- **{corr['var1']}** ↔ **{corr['var2']}**: {corr['correlation']:.3f}")
                        
                        # Generate insights
                        with st.spinner("🧠 Generating AI insights..."):
                            insights = st.session_state.router.data_analyzer.generate_insights()
                            result_card("AI Insights", insights, "info")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with tab4:
            st.markdown("#### Custom Visualizations")
            st.markdown("Select columns to visualize:")
            
            # Get available columns
            df = st.session_state.router.data_analyzer.df
            all_columns = df.columns.tolist()
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            # Column selection
            col1, col2, col3 = st.columns(3)
            
            with col1:
                x_column = st.selectbox(
                    "X Axis (Category/Time):",
                    options=[None] + all_columns,
                    key="viz_x"
                )
            
            with col2:
                y_column = st.selectbox(
                    "Y Axis (Value):",
                    options=[None] + all_columns,
                    key="viz_y"
                )
            
            with col3:
                color_column = st.selectbox(
                    "Color / Group (Optional):",
                    options=[None] + all_columns,
                    key="viz_color"
                )
            
            # Chart type
            st.markdown("---")
            chart_type = st.radio(
                "Chart Type:",
                options=["Bar Chart", "Pie Chart", "Line Chart", "Box Plot", "Scatter Plot"],
                horizontal=True,
                key="chart_selector"
            )
            
            # Generate button
            if st.button("📊 Create Chart", key="gen_chart", type="primary"):
                try:
                    import plotly.express as px
                    
                    st.markdown("---")
                    
                    # Prepare data (copy to avoid modifying original)
                    plot_df = df.copy()
                    
                    # 1. BAR CHART
                    if chart_type == "Bar Chart":
                        if x_column and y_column:
                            if y_column in numeric_columns:
                                # X = Cat, Y = Num -> Sum Y by X
                                if color_column:
                                    plot_df = plot_df.groupby([x_column, color_column])[y_column].sum().reset_index()
                                else:
                                    plot_df = plot_df.groupby(x_column)[y_column].sum().reset_index()
                                
                                fig = px.bar(plot_df, x=x_column, y=y_column, color=color_column, 
                                           title=f"Sum of {y_column} by {x_column}")
                            else:
                                # X = Cat, Y = Cat -> Count occurrences
                                plot_df = plot_df.groupby([x_column, y_column]).size().reset_index(name='Count')
                                fig = px.bar(plot_df, x=x_column, y='Count', color=y_column, 
                                           title=f"Count of {y_column} by {x_column}")
                        
                        elif x_column:
                            # Only X -> Count X
                            count_df = plot_df[x_column].value_counts().reset_index()
                            count_df.columns = [x_column, 'Count']
                            fig = px.bar(count_df.head(50), x=x_column, y='Count', color=color_column if color_column else None,
                                       title=f"Count of {x_column}")
                        
                        elif y_column:
                            # Only Y -> Plot Y values (if numeric) or Count Y (if cat)
                            if y_column in numeric_columns:
                                fig = px.bar(plot_df.head(100), y=y_column, color=color_column, 
                                           title=f"{y_column} Values (First 100)")
                            else:
                                count_df = plot_df[y_column].value_counts().reset_index()
                                count_df.columns = [y_column, 'Count']
                                fig = px.bar(count_df.head(50), x=y_column, y='Count', color=color_column,
                                           title=f"Count of {y_column}")
                        else:
                            st.warning("Please select at least X or Y column.")
                            fig = None

                    # 2. PIE CHART
                    elif chart_type == "Pie Chart":
                        if x_column and y_column and y_column in numeric_columns:
                            # Sum Y by X
                            pie_df = plot_df.groupby(x_column)[y_column].sum().reset_index()
                            fig = px.pie(pie_df, names=x_column, values=y_column, 
                                       title=f"Distribution of {y_column} by {x_column}")
                        elif x_column:
                            # Count X
                            fig = px.pie(plot_df, names=x_column, title=f"Count Distribution of {x_column}")
                        elif y_column and y_column not in numeric_columns:
                            # Count Y
                            fig = px.pie(plot_df, names=y_column, title=f"Count Distribution of {y_column}")
                        else:
                            st.warning("For Pie Chart: Select X (Category) and optionally Y (Value).")
                            fig = None

                    # 3. LINE CHART
                    elif chart_type == "Line Chart":
                        if y_column and y_column in numeric_columns:
                            if x_column:
                                fig = px.line(plot_df, x=x_column, y=y_column, color=color_column, 
                                            title=f"{y_column} over {x_column}")
                            else:
                                fig = px.line(plot_df, y=y_column, color=color_column, 
                                            title=f"{y_column} Trend")
                        else:
                            st.warning("Line Chart requires a numeric Y column.")
                            fig = None

                    # 4. BOX PLOT
                    elif chart_type == "Box Plot":
                        if y_column and y_column in numeric_columns:
                            fig = px.box(plot_df, x=x_column, y=y_column, color=color_column, 
                                       title=f"Distribution of {y_column}")
                        else:
                            st.warning("Box Plot requires a numeric Y column.")
                            fig = None

                    # 5. SCATTER PLOT
                    elif chart_type == "Scatter Plot":
                        if x_column and y_column:
                            fig = px.scatter(plot_df, x=x_column, y=y_column, color=color_column, 
                                           title=f"{y_column} vs {x_column}")
                        else:
                            st.warning("Scatter Plot requires both X and Y columns.")
                            fig = None

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        st.success(f"✅ {chart_type} created!")
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("💡 Try selecting different columns.")

        with tab5:
            st.markdown("#### 🔍 Outlier Detection (All Columns)")
            st.markdown("Analyze outliers across all numeric columns using Z-Score and IQR methods.")
            
            # Get numeric columns
            df = st.session_state.router.data_analyzer.df
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            if len(numeric_columns) == 0:
                st.warning("⚠️ No numeric columns found in the dataset.")
            else:
                st.info(f"📊 Found {len(numeric_columns)} numeric columns to analyze")
                
                if st.button("🔍 Detect Outliers (All Columns)", key="detect_all_outliers", type="primary"):
                    with st.spinner("Analyzing all columns..."):
                        try:
                            # Analyze all columns
                            results = []
                            
                            for col in numeric_columns:
                                # Get stats
                                analysis = st.session_state.router.data_analyzer.analyze_outliers(col)
                                stats = analysis['stats']
                                suggestion = analysis['suggestion']
                                
                                # Detect outliers using both methods
                                zscore_results = st.session_state.router.data_analyzer.detect_outliers_zscore(col)
                                iqr_results = st.session_state.router.data_analyzer.detect_outliers_iqr(col)
                                
                                results.append({
                                    'Column': col,
                                    'Mean': f"{stats['mean']:.2f}",
                                    'Median': f"{stats['median']:.2f}",
                                    'Std Dev': f"{stats['std']:.2f}",
                                    'Skewness': f"{stats['skewness']:.2f}",
                                    'Z-Score Outliers': f"{zscore_results['outlier_count']} ({zscore_results['percentage']:.1f}%)",
                                    'IQR Outliers': f"{iqr_results['outlier_count']} ({iqr_results['percentage']:.1f}%)",
                                    'Recommended': suggestion['method']
                                })
                            
                            # Store results in session state
                            st.session_state['all_outlier_results'] = results
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Display results if they exist
                if 'all_outlier_results' in st.session_state:
                    st.markdown("---")
                    st.markdown("##### 📊 Outlier Detection Results (Column-wise)")
                    
                    import pandas as pd
                    results_df = pd.DataFrame(st.session_state['all_outlier_results'])
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Summary statistics
                    st.markdown("---")
                    st.markdown("##### 📈 Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_zscore = sum([int(r['Z-Score Outliers'].split('(')[0].strip()) for r in st.session_state['all_outlier_results']])
                        st.metric("Total Z-Score Outliers", total_zscore)
                    
                    with col2:
                        total_iqr = sum([int(r['IQR Outliers'].split('(')[0].strip()) for r in st.session_state['all_outlier_results']])
                        st.metric("Total IQR Outliers", total_iqr)
                    
                    with col3:
                        zscore_rec = sum([1 for r in st.session_state['all_outlier_results'] if r['Recommended'] == 'Z-Score'])
                        iqr_rec = len(st.session_state['all_outlier_results']) - zscore_rec
                        st.metric("Columns Needing IQR", iqr_rec)
                    
                    # Column-specific analysis
                    st.markdown("---")
                    st.markdown("##### 🔬 Detailed Analysis")
                    st.markdown("Select a column to see detailed outlier information:")
                    
                    selected_col = st.selectbox(
                        "Column:",
                        options=numeric_columns,
                        key="detailed_column"
                    )
                    
                    if selected_col:
                        method_tab1, method_tab2 = st.tabs(["Z-Score Method", "IQR Method"])
                        
                        # Z-SCORE TAB
                        with method_tab1:
                            try:
                                import plotly.express as px
                                
                                zscore_results = st.session_state.router.data_analyzer.detect_outliers_zscore(selected_col)
                                
                                st.metric(
                                    "Outliers Detected (Z-Score > 3)", 
                                    f"{zscore_results['outlier_count']} ({zscore_results['percentage']:.2f}%)"
                                )
                                
                                # Visualizations
                                viz_col1, viz_col2 = st.columns(2)
                                
                                with viz_col1:
                                    st.markdown("**📦 Boxplot**")
                                    fig_box = px.box(df, y=selected_col, title=f"Boxplot: {selected_col}")
                                    st.plotly_chart(fig_box, use_container_width=True, key=f"zscore_box_{selected_col}")
                                
                                with viz_col2:
                                    st.markdown("**📊 Distribution**")
                                    fig_hist = px.histogram(df, x=selected_col, nbins=30, title=f"Distribution: {selected_col}")
                                    st.plotly_chart(fig_hist, use_container_width=True, key=f"zscore_hist_{selected_col}")
                                
                                # Explainability
                                if not zscore_results['explainability'].empty:
                                    st.markdown("**🔬 Outlier Details (Top 10)**")
                                    st.dataframe(zscore_results['explainability'], use_container_width=True)
                                    
                                    if st.button(f"🗑️ Remove {zscore_results['outlier_count']} Outliers (Z-Score)", key="remove_zscore_detailed"):
                                        with st.spinner("Removing outliers..."):
                                            st.session_state.router.data_analyzer.remove_outliers(zscore_results['outlier_indices'])
                                            st.success(f"✅ Removed {zscore_results['outlier_count']} outliers!")
                                            del st.session_state['all_outlier_results']
                                            st.rerun()
                                else:
                                    st.success("✅ No outliers detected!")
                            
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                        
                        # IQR TAB
                        with method_tab2:
                            try:
                                import plotly.express as px
                                
                                iqr_results = st.session_state.router.data_analyzer.detect_outliers_iqr(selected_col)
                                
                                st.metric(
                                    "Outliers Detected (IQR Method)", 
                                    f"{iqr_results['outlier_count']} ({iqr_results['percentage']:.2f}%)"
                                )
                                
                                # IQR Info
                                info_col1, info_col2, info_col3 = st.columns(3)
                                with info_col1:
                                    st.metric("Q1", f"{iqr_results['Q1']:.2f}")
                                with info_col2:
                                    st.metric("Q3", f"{iqr_results['Q3']:.2f}")
                                with info_col3:
                                    st.metric("IQR", f"{iqr_results['IQR']:.2f}")
                                
                                # Visualizations
                                viz_col1, viz_col2 = st.columns(2)
                                
                                with viz_col1:
                                    st.markdown("**📦 Boxplot**")
                                    fig_box = px.box(df, y=selected_col, title=f"Boxplot: {selected_col}")
                                    st.plotly_chart(fig_box, use_container_width=True, key=f"iqr_box_{selected_col}")
                                
                                with viz_col2:
                                    st.markdown("**📊 Distribution**")
                                    fig_hist = px.histogram(df, x=selected_col, nbins=30, title=f"Distribution: {selected_col}")
                                    st.plotly_chart(fig_hist, use_container_width=True, key=f"iqr_hist_{selected_col}")
                                
                                # Explainability
                                if not iqr_results['explainability'].empty:
                                    st.markdown("**🔬 Outlier Details (Top 10)**")
                                    st.dataframe(iqr_results['explainability'], use_container_width=True)
                                    
                                    if st.button(f"🗑️ Remove {iqr_results['outlier_count']} Outliers (IQR)", key="remove_iqr_detailed"):
                                        with st.spinner("Removing outliers..."):
                                            st.session_state.router.data_analyzer.remove_outliers(iqr_results['outlier_indices'])
                                            st.success(f"✅ Removed {iqr_results['outlier_count']} outliers!")
                                            del st.session_state['all_outlier_results']
                                            st.rerun()
                                else:
                                    st.success("✅ No outliers detected!")
                            
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    # Undo functionality
                    st.markdown("---")
                    st.markdown("##### ↩️ Undo Changes")
                    if st.button("🔄 Reload Original Data", key="reload_data_all"):
                        with st.spinner("Reloading data..."):
                            file_path = st.session_state.router.data_analyzer.file_path
                            st.session_state.router.data_analyzer.load_data(file_path)
                            st.success("✅ Original data reloaded!")
                            if 'all_outlier_results' in st.session_state:
                                del st.session_state['all_outlier_results']
                            st.rerun()
            



# ============================================
# MODE 4: VOICE GENERATION
# ============================================




# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """
    Main application entry point.
    """
    # Initialize session state
    initialize_session_state()
    
    # Display logo
    display_logo()
    
    # Check if router initialized successfully
    if not st.session_state.get('router_initialized', False):
        st.error("⚠️ Failed to initialize Cognivault AI Agent")
        st.error(f"Error: {st.session_state.get('router_error', 'Unknown error')}")
        st.info("💡 Please check your .env file and ensure all API keys are set correctly.")
        st.stop()
    
    # Sidebar
    # Mode selection
    selected_mode = st.radio(
        "Select Mode:",
        options=[
            "🎯 Business Consulting",
            "📄 Document Q&A",
            "📊 Data Analysis"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="mode_selection"
    )
    
    # Execute selected mode
    if "Business Consulting" in selected_mode:
        st.session_state.current_mode = "Business Consulting"
        business_consulting_mode()
        
    elif "Document Q&A" in selected_mode:
        st.session_state.current_mode = "Document Q&A"
        rag_documents_mode()
        
    elif "Data Analysis" in selected_mode:
        st.session_state.current_mode = "Data Analysis"
        data_analysis_mode()
    
    # Sidebar (called after mode update to show correct state)
    sidebar_info()


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()
