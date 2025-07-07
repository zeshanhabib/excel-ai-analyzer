import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from excel_reader import ExcelReader
from google_sheets_reader import GoogleSheetsReader, UnifiedDataReader
from ai_analyzer import AIAnalyzer
from visualizer import DataVisualizer
from utils import (
    setup_logging, validate_dataframe, detect_column_types,
    suggest_data_cleaning, create_data_profile_report, format_number
)
import os
import json
import tempfile
from typing import Dict, Any, Optional
import logging

# Configure page
st.set_page_config(
    page_title="Excel AI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = None
if 'data_reader' not in st.session_state:
    st.session_state.data_reader = None

def initialize_google_sheets():
    """Initialize Google Sheets integration."""
    st.sidebar.subheader("🔧 Google Sheets Setup")
    
    # Option 1: Upload service account JSON
    uploaded_creds = st.sidebar.file_uploader(
        "Upload Service Account JSON",
        type=['json'],
        help="Upload your Google Cloud service account credentials"
    )
    
    if uploaded_creds:
        try:
            import json
            credentials_dict = json.load(uploaded_creds)
            st.session_state.data_reader = UnifiedDataReader(
                google_credentials_dict=credentials_dict
            )
            st.sidebar.success("✅ Google Sheets credentials loaded")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error loading credentials: {str(e)}")
            return False
    
    # Option 2: Environment variable
    elif os.getenv('GOOGLE_SHEETS_CREDENTIALS'):
        try:
            st.session_state.data_reader = UnifiedDataReader()
            st.sidebar.success("✅ Google Sheets initialized from environment")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error initializing Google Sheets: {str(e)}")
            return False
    
    # Option 3: Manual credentials input
    else:
        with st.sidebar.expander("🔐 Manual Credentials Setup"):
            st.markdown("""
            **To use Google Sheets:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a service account
            3. Download the JSON credentials
            4. Upload the file above
            
            **Or set environment variable:**
            ```
            GOOGLE_SHEETS_CREDENTIALS='{"type": "service_account", ...}'
            ```
            """)
        return False

def generate_google_sheets_samples():
    """Generate sample data in Google Sheets for testing."""
    st.sidebar.subheader("🎯 Generate Sample Google Sheets")
    
    if not st.session_state.data_reader or not hasattr(st.session_state.data_reader, 'google_reader'):
        st.sidebar.warning("⚠️ Google Sheets not configured. Upload credentials first.")
        return
    
    with st.sidebar.expander("📊 Create Sample Sheets"):
        st.write("Generate sample datasets directly in Google Sheets:")
        
        sample_types = st.multiselect(
            "Select datasets to create:",
            ["📈 Sales Data (1000 records)", "👥 Employee Data (500 records)", 
             "📦 Inventory Data (300 records)", "📋 Multi-Sheet Demo"],
            default=["📋 Multi-Sheet Demo"]
        )
        
        if st.button("🚀 Generate Sample Sheets", key="generate_sheets"):
            if not sample_types:
                st.error("Please select at least one dataset type.")
                return
                
            with st.spinner("Creating Google Sheets..."):
                try:
                    from create_sample_data import generate_sales_data, generate_employee_data, generate_inventory_data
                    import gspread
                    
                    # Get the authenticated client
                    client = st.session_state.data_reader.google_reader.client
                    if not client:
                        st.error("❌ Not authenticated with Google Sheets")
                        return
                    
                    created_sheets = []
                    
                    # Generate Sales Data
                    if "📈 Sales Data (1000 records)" in sample_types:
                        sales_df = generate_sales_data(1000)
                        sales_sheet = create_google_sheet(client, "Excel AI - Sample Sales Data", {"Sales": sales_df})
                        if sales_sheet:
                            created_sheets.append(("Sales Data", sales_sheet))
                    
                    # Generate Employee Data  
                    if "👥 Employee Data (500 records)" in sample_types:
                        employee_df = generate_employee_data(500)
                        emp_sheet = create_google_sheet(client, "Excel AI - Sample Employee Data", {"Employees": employee_df})
                        if emp_sheet:
                            created_sheets.append(("Employee Data", emp_sheet))
                    
                    # Generate Inventory Data
                    if "📦 Inventory Data (300 records)" in sample_types:
                        inventory_df = generate_inventory_data(300)
                        inv_sheet = create_google_sheet(client, "Excel AI - Sample Inventory Data", {"Inventory": inventory_df})
                        if inv_sheet:
                            created_sheets.append(("Inventory Data", inv_sheet))
                    
                    # Generate Multi-Sheet Demo
                    if "📋 Multi-Sheet Demo" in sample_types:
                        sales_df = generate_sales_data(100)
                        employee_df = generate_employee_data(50)
                        inventory_df = generate_inventory_data(30)
                        summary_df = pd.DataFrame({
                            'Dataset': ['Sales', 'Employees', 'Inventory'],
                            'Records': [100, 50, 30],
                            'Purpose': ['Product sales analysis', 'HR analytics', 'Stock management']
                        })
                        
                        multi_data = {
                            "Sales": sales_df,
                            "Employees": employee_df, 
                            "Inventory": inventory_df,
                            "Summary": summary_df
                        }
                        multi_sheet = create_google_sheet(client, "Excel AI - Multi-Sheet Demo", multi_data)
                        if multi_sheet:
                            created_sheets.append(("Multi-Sheet Demo", multi_sheet))
                    
                    # Display results
                    if created_sheets:
                        st.success(f"✅ Created {len(created_sheets)} sample spreadsheet(s)!")
                        st.write("**Created Spreadsheets:**")
                        for name, url in created_sheets:
                            st.write(f"• [{name}]({url})")
                        
                        # Save URLs for reference
                        urls_text = "Excel AI - Sample Google Sheets\n" + "="*40 + "\n\n"
                        for name, url in created_sheets:
                            urls_text += f"{name}: {url}\n"
                        
                        st.download_button(
                            "📄 Download URLs",
                            urls_text,
                            file_name="sample_google_sheets_urls.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("❌ No spreadsheets were created successfully.")
                        
                except Exception as e:
                    st.error(f"❌ Error creating sample sheets: {str(e)}")
                    logger.error(f"Sample sheets creation error: {str(e)}")

def create_google_sheet(client, title: str, sheets_data: Dict[str, pd.DataFrame]) -> Optional[str]:
    """Create a Google Sheet with the provided data."""
    try:
        # Create new spreadsheet
        spreadsheet = client.create(title)
        
        # Get the default sheet and rename it
        default_sheet = spreadsheet.sheet1
        first_sheet_name = list(sheets_data.keys())[0]
        default_sheet.update_title(first_sheet_name)
        
        # Add data to the first sheet
        first_df = sheets_data[first_sheet_name]
        populate_google_sheet(default_sheet, first_df)
        
        # Add remaining sheets
        for sheet_name, df in list(sheets_data.items())[1:]:
            new_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=len(df)+10, cols=len(df.columns)+5)
            populate_google_sheet(new_sheet, df)
        
        # Make spreadsheet shareable
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        
    except Exception as e:
        logger.error(f"Failed to create Google Sheet '{title}': {str(e)}")
        return None

def populate_google_sheet(sheet, df: pd.DataFrame):
    """Populate a Google Sheet with DataFrame data."""
    # Convert DataFrame to list of lists
    values = [df.columns.tolist()] + df.values.tolist()
    
    # Update the sheet with data
    sheet.clear()
    sheet.update('A1', values)
    
    # Format headers
    sheet.format('1:1', {
        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
    })

def load_data_source() -> Optional[pd.DataFrame]:
    """Load data from various sources (Excel files, Google Sheets, etc)."""
    
    # Initialize data reader if not already done
    if not st.session_state.data_reader:
        google_available = initialize_google_sheets()
        if not google_available:
            # Fallback to Excel-only reader
            st.session_state.data_reader = UnifiedDataReader()
    
    # Data source selection
    st.sidebar.subheader("📊 Data Source")
    source_type = st.sidebar.radio(
        "Choose data source:",
        ["📁 Upload Excel File", "🔗 Google Sheets URL", "🎯 Sample Data"]
    )
    
    if source_type == "📁 Upload Excel File":
        uploaded_file = st.sidebar.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file to analyze"
        )
        
        if uploaded_file:
            return load_excel_file(uploaded_file)
    
    elif source_type == "🔗 Google Sheets URL":
        sheets_url = st.sidebar.text_input(
            "Google Sheets URL or ID",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Paste the Google Sheets URL or just the sheet ID"
        )
        
        if sheets_url:
            return load_google_sheets(sheets_url)
    
    elif source_type == "🎯 Sample Data":
        sample_files = {
            "Sales Data": "sample_data/sales_data.xlsx",
            "Employee Data": "sample_data/employee_data.xlsx", 
            "Inventory Data": "sample_data/inventory_data.xlsx",
            "Multi-sheet Example": "sample_data/multi_sheet_example.xlsx"
        }
        
        selected_sample = st.sidebar.selectbox(
            "Choose sample dataset:",
            list(sample_files.keys())
        )
        
        if st.sidebar.button("Load Sample Data"):
            file_path = sample_files[selected_sample]
            if os.path.exists(file_path):
                try:
                    sheets = st.session_state.data_reader.read_data(file_path)
                    if len(sheets) > 1:
                        sheet_names = list(sheets.keys())
                        selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)
                        return sheets[selected_sheet]
                    else:
                        return list(sheets.values())[0]
                except Exception as e:
                    st.sidebar.error(f"Error loading sample data: {str(e)}")
                    return None
            else:
                st.sidebar.error("Sample data not found. Run create_sample_data.py first.")
                return None
    
    return None

def load_google_sheets(sheets_url: str) -> Optional[pd.DataFrame]:
    """Load data from Google Sheets."""
    try:
        if not st.session_state.data_reader:
            st.error("Google Sheets not configured. Please set up credentials in the sidebar.")
            return None
        
        with st.spinner("📡 Connecting to Google Sheets..."):
            # Validate access first
            if not st.session_state.data_reader.validate_source(sheets_url):
                st.error("❌ Cannot access Google Sheets. Check URL and permissions.")
                return None
            
            # Get available worksheets
            try:
                google_reader = st.session_state.data_reader.google_reader
                worksheets = google_reader.get_available_worksheets(sheets_url)
                
                if len(worksheets) > 1:
                    selected_worksheet = st.sidebar.selectbox(
                        "Select Worksheet", 
                        worksheets,
                        key="worksheet_selector"
                    )
                    sheets = st.session_state.data_reader.read_data(sheets_url, selected_worksheet)
                    return sheets[selected_worksheet]
                else:
                    sheets = st.session_state.data_reader.read_data(sheets_url)
                    return list(sheets.values())[0] if sheets else None
                    
            except Exception as e:
                st.error(f"Error reading Google Sheets: {str(e)}")
                return None
                
    except Exception as e:
        st.error(f"Google Sheets error: {str(e)}")
        return None

def initialize_ai_analyzer():
    """Initialize AI analyzer with API key."""
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to enable AI analysis"
    )
    
    if api_key:
        try:
            st.session_state.ai_analyzer = AIAnalyzer(api_key=api_key)
            st.sidebar.success("✅ AI Analyzer initialized")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error initializing AI: {str(e)}")
            return False
    elif os.getenv("OPENAI_API_KEY"):
        try:
            st.session_state.ai_analyzer = AIAnalyzer()
            st.sidebar.success("✅ AI Analyzer initialized from environment")
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error initializing AI: {str(e)}")
            return False
    else:
        st.sidebar.warning("⚠️ Enter OpenAI API key to enable AI features")
        return False

def load_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Load and process uploaded Excel file."""
    if uploaded_file is not None:
        try:
            import tempfile
            
            # Create a temporary file with proper cleanup
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name
            
            try:
                # Read Excel file
                excel_reader = ExcelReader()
                sheets = excel_reader.read_excel(tmp_file_path)
                
                # Handle multiple sheets
                if len(sheets) > 1:
                    sheet_names = list(sheets.keys())
                    selected_sheet = st.selectbox("Select Sheet", sheet_names)
                    return sheets[selected_sheet]
                else:
                    return list(sheets.values())[0]
                    
            finally:
                # Always clean up temp file
                try:
                    os.remove(tmp_file_path)
                except OSError:
                    pass  # File already deleted or not accessible
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            logger.error(f"Excel file loading error: {str(e)}")
            return None
    return None

def display_data_overview(df: pd.DataFrame):
    """Display comprehensive data overview."""
    st.subheader("📋 Data Overview")
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("Missing Data", f"{missing_pct:.1f}%")
    with col4:
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.metric("Memory Usage", f"{memory_mb:.1f} MB")
    
    # Column information
    with st.expander("📊 Column Details", expanded=False):
        column_info = detect_column_types(df)
        
        col_df = pd.DataFrame([
            {
                'Column': col,
                'Type': info['semantic_type'],
                'Dtype': info['dtype'],
                'Missing %': f"{info['null_percentage']:.1f}%",
                'Unique Values': info['unique_count'],
                'Unique %': f"{info['unique_percentage']:.1f}%"
            }
            for col, info in column_info.items()
        ])
        
        st.dataframe(col_df, use_container_width=True)
    
    # Data quality suggestions
    cleaning_suggestions = suggest_data_cleaning(df)
    if cleaning_suggestions:
        with st.expander("🔧 Data Quality Suggestions", expanded=False):
            for suggestion in cleaning_suggestions:
                if suggestion['type'] == 'high_nulls':
                    st.warning(f"⚠️ {suggestion['column']}: {suggestion['suggestion']}")
                elif suggestion['type'] == 'duplicates':
                    st.info(f"ℹ️ {suggestion['suggestion']}")
                else:
                    st.info(f"💡 {suggestion.get('column', 'General')}: {suggestion['suggestion']}")

def display_ai_analysis(df: pd.DataFrame):
    """Display AI-powered analysis section."""
    if not st.session_state.ai_analyzer:
        st.warning("⚠️ AI analysis requires OpenAI API key. Please configure it in the sidebar.")
        return
    
    st.subheader("🤖 AI Analysis")
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💡 Data Insights", "❓ Ask Questions", "🔍 Anomaly Detection", "🐛 Debug Report"])
    
    with tab1:
        if st.button("Generate AI Insights", type="primary"):
            with st.spinner("🧠 Analyzing data with AI..."):
                try:
                    analysis = st.session_state.ai_analyzer.analyze_data_structure(df)
                    st.session_state.analysis_results['structure_analysis'] = analysis
                    
                    if 'ai_analysis' in analysis:
                        st.markdown("### 📊 AI Analysis Results")
                        st.markdown(analysis['ai_analysis'])
                    else:
                        st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error in AI analysis: {str(e)}")
        
        # Display previous analysis if available
        if 'structure_analysis' in st.session_state.analysis_results:
            analysis = st.session_state.analysis_results['structure_analysis']
            if 'ai_analysis' in analysis:
                st.markdown("### 📊 Previous Analysis Results")
                st.markdown(analysis['ai_analysis'])
    
    with tab2:
        user_question = st.text_area(
            "Ask a question about your data:",
            placeholder="e.g., What are the top 5 products by sales? What trends do you see in the data?",
            height=100
        )
        
        if st.button("Get AI Answer") and user_question:
            print(f"DEBUG APP: AI Answer button clicked with question: '{user_question}'")
            print(f"DEBUG APP: DataFrame shape: {df.shape}")
            print(f"DEBUG APP: AI analyzer exists: {st.session_state.ai_analyzer is not None}")
            
            with st.spinner("🤔 Thinking..."):
                try:
                    print("DEBUG APP: About to call answer_question")
                    answer = st.session_state.ai_analyzer.answer_question(df, user_question)
                    print(f"DEBUG APP: Got answer: {answer}")
                    
                    st.markdown("### 💬 AI Response")
                    if 'answer' in answer:
                        st.markdown(answer['answer'])
                        
                        # Display supporting data if available
                        if answer.get('supporting_data'):
                            with st.expander("📈 Supporting Data"):
                                st.json(answer['supporting_data'])
                    else:
                        st.error(f"Failed to answer: {answer.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")
    
    with tab3:
        if st.button("Detect Anomalies"):
            with st.spinner("🔍 Detecting anomalies..."):
                try:
                    anomalies = st.session_state.ai_analyzer.detect_anomalies(df)
                    
                    if 'anomalies' in anomalies and anomalies['anomalies']:
                        st.markdown("### 🚨 Anomalies Detected")
                        
                        for col, info in anomalies['anomalies'].items():
                            with st.expander(f"📊 {col} - {info['count']} anomalies ({info['percentage']:.1f}%)"):
                                st.write(f"**Outlier bounds:** {info['bounds']['lower']:.2f} to {info['bounds']['upper']:.2f}")
                                st.write(f"**Sample outlier values:** {info['outlier_values'][:5]}")
                        
                        st.markdown("### 🧠 AI Interpretation")
                        st.markdown(anomalies['ai_interpretation'])
                    else:
                        st.success("✅ No significant anomalies detected!")
                        if 'ai_interpretation' in anomalies:
                            st.info(anomalies['ai_interpretation'])
                except Exception as e:
                    st.error(f"Error detecting anomalies: {str(e)}")

def display_visualizations(df: pd.DataFrame):
    """Display data visualizations."""
    st.subheader("📈 Data Visualizations")
    
    visualizer = DataVisualizer()
    
    # Get AI suggestions for visualizations
    if st.session_state.ai_analyzer:
        if st.button("🤖 Get AI Visualization Suggestions"):
            with st.spinner("Getting AI suggestions..."):
                try:
                    suggestions = st.session_state.ai_analyzer.suggest_visualizations(df)
                    st.session_state.viz_suggestions = suggestions
                except Exception as e:
                    st.error(f"Error getting suggestions: {str(e)}")
    
    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Smart Suggestions", "📊 Custom Charts", "🔍 Quick Views"])
    
    with tab1:
        # Display AI suggestions
        if hasattr(st.session_state, 'viz_suggestions'):
            for i, suggestion in enumerate(st.session_state.viz_suggestions):
                if suggestion.get('type') != 'error':
                    with st.expander(f"📊 {suggestion.get('title', f'Suggestion {i+1}')}"):
                        st.write(suggestion.get('description', ''))
                        if isinstance(suggestion, list) and len(suggestion) > 0 and 'description' in suggestion[0]:
                            st.write(suggestion[0]['description'])
        
        # Auto-generated visualizations
        suggestions = visualizer.suggest_best_visualizations(df)
        
        for suggestion in suggestions[:3]:  # Show first 3 suggestions
            try:
                fig = visualizer.create_visualization_from_suggestion(df, suggestion)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating {suggestion['type']} chart: {str(e)}")
    
    with tab2:
        # Custom chart builder
        st.markdown("#### 🔧 Build Custom Charts")
        
        chart_type = st.selectbox(
            "Chart Type",
            ["Scatter Plot", "Bar Chart", "Line Chart", "Box Plot", "Correlation Matrix"]
        )
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X-axis", numeric_cols)
            with col2:
                y_col = st.selectbox("Y-axis", [col for col in numeric_cols if col != x_col])
            
            color_col = st.selectbox("Color by (optional)", [None] + categorical_cols)
            
            if st.button("Create Scatter Plot"):
                fig = visualizer.create_scatter_plot(df, x_col, y_col, color_col)
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Bar Chart" and len(categorical_cols) > 0 and len(numeric_cols) > 0:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("Category", categorical_cols)
            with col2:
                y_col = st.selectbox("Value", numeric_cols)
            
            if st.button("Create Bar Chart"):
                fig = visualizer.create_bar_chart(df, x_col, y_col)
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Correlation Matrix":
            if st.button("Create Correlation Matrix"):
                fig = visualizer.create_correlation_matrix(df)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Quick overview charts
        if st.button("📊 Generate Overview Dashboard"):
            with st.spinner("Creating dashboard..."):
                fig = visualizer.create_overview_dashboard(df)
                st.plotly_chart(fig, use_container_width=True)
        
        if len(numeric_cols) > 0:
            if st.button("📦 Box Plots (Outlier Detection)"):
                fig = visualizer.create_box_plot(df, numeric_cols[:5])  # Limit to 5 columns
                st.plotly_chart(fig, use_container_width=True)

def setup_debug_controls():
    """Setup debugging controls in sidebar."""
    import config
    
    st.sidebar.subheader("🔧 Debug Settings")
    
    # Debug level selection
    debug_level_names = ['MINIMAL', 'STANDARD', 'DETAILED', 'FULL']
    current_level_name = next((name for name, level in config.DEBUG_LEVELS.items() 
                              if level == config.DEBUG_LEVEL), 'STANDARD')
    
    selected_level = st.sidebar.selectbox(
        "Debug Level",
        debug_level_names,
        index=debug_level_names.index(current_level_name),
        help="Control the amount of debugging information captured"
    )
    
    # Update config with selected level
    config.DEBUG_LEVEL = config.DEBUG_LEVELS[selected_level]
    
    # Debug options
    debug_options = st.sidebar.expander("🔍 Advanced Debug Options")
    with debug_options:
        config.AI_USE_FULL_DATASET = st.checkbox(
            "Use Full Dataset for AI", 
            value=config.AI_USE_FULL_DATASET,
            help="Use complete dataset instead of samples for AI analysis"
        )
        
        config.DEBUG_TRACK_DATA_SIZE = st.checkbox(
            "Track Data Sizes", 
            value=config.DEBUG_TRACK_DATA_SIZE,
            help="Track data sizes at each processing step"
        )
        
        config.DEBUG_TRACK_AI_PROMPTS = st.checkbox(
            "Track AI Prompts", 
            value=config.DEBUG_TRACK_AI_PROMPTS,
            help="Log AI prompt construction and responses"
        )
        
        config.DEBUG_SAVE_DEBUG_LOGS = st.checkbox(
            "Save Debug Logs", 
            value=config.DEBUG_SAVE_DEBUG_LOGS,
            help="Save detailed debug logs to file"
        )
    
    # Show current debug status
    if config.DEBUG_LEVEL > 0:
        debug_status = debug_options.container()
        debug_status.info(f"🐛 Debug Level: {selected_level} (Level {config.DEBUG_LEVEL})")
        
        if config.AI_USE_FULL_DATASET:
            debug_status.success("✅ Using full datasets for AI analysis")
        else:
            debug_status.warning("⚠️ Using data samples for AI analysis")

# ...existing code...

def main():
    """Main application function."""
    # Header
    st.title("📊 Excel AI Analyzer")
    st.markdown("Upload an Excel file and get AI-powered insights, analysis, and visualizations!")
    
    # Sidebar
    st.sidebar.title("🔧 Configuration")
    
    # Initialize AI analyzer
    initialize_ai_analyzer()
    
    # Google Sheets sample generation
    generate_google_sheets_samples()
    
    # Debug controls
    setup_debug_controls()
    
    # Load data from various sources
    df = load_data_source()
    
    if df is not None:
            st.session_state.data = df
            
            # Validate data
            is_valid, error_msg = validate_dataframe(df)
            if not is_valid:
                st.error(f"Data validation failed: {error_msg}")
                return
            
            # Display data sample
            with st.expander("👀 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Main content tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Overview",
                "🤖 AI Analysis", 
                "📈 Visualizations",
                "📊 Data Export"
            ])
            
            with tab1:
                display_data_overview(df)
            
            with tab2:
                display_ai_analysis(df)
            
            with tab3:
                display_visualizations(df)
            
            with tab4:
                st.subheader("📤 Export Results")
                
                # Generate comprehensive report
                if st.button("📋 Generate Data Profile Report"):
                    with st.spinner("Generating report..."):
                        report = create_data_profile_report(df)
                        st.json(report)
                
                # Download options
                st.markdown("#### 💾 Download Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📄 Download as CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="analyzed_data.csv",
                            mime="text/csv"
                        )
                
                with col2:
                    if st.button("📊 Download as Excel"):
                        from io import BytesIO
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Data', index=False)
                        
                        st.download_button(
                            label="Download Excel",
                            data=output.getvalue(),
                            file_name="analyzed_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 Welcome to Excel AI Analyzer!
        
        This powerful tool helps you:
        
        - 📊 **Analyze Excel Data**: Upload and explore your Excel files with detailed insights
        - 🤖 **AI-Powered Analysis**: Get intelligent insights and answers to your data questions
        - 📈 **Smart Visualizations**: Automatically generate the best charts for your data
        - 🔍 **Anomaly Detection**: Identify outliers and data quality issues
        - 💬 **Natural Language Queries**: Ask questions about your data in plain English
        
        ### 🏁 Getting Started:
        1. **Configure AI** (optional): Add your OpenAI API key in the sidebar for AI features
        2. **Upload Excel File**: Use the file uploader in the sidebar
        3. **Explore & Analyze**: Navigate through the tabs to explore your data
        
        ### 📋 Supported Features:
        - Excel files (.xlsx, .xls)
        - Multiple sheet support
        - Data quality assessment
        - Statistical analysis
        - Interactive visualizations
        - AI-powered insights
        """)
        
        # Sample data section
        st.markdown("### 📊 Try with Sample Data")
        if st.button("🎯 Load Sample Sales Data"):
            # Create sample data
            import numpy as np
            np.random.seed(42)
            
            sample_data = pd.DataFrame({
                'Product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'] * 20,
                'Sales': np.random.normal(1000, 200, 100),
                'Region': ['North', 'South', 'East', 'West'] * 25,
                'Month': pd.date_range('2023-01-01', periods=100, freq='D'),
                'Price': np.random.uniform(10, 100, 100),
                'Quantity': np.random.poisson(10, 100)
            })
            
            st.session_state.data = sample_data
            st.success("✅ Sample data loaded! Explore the tabs above.")
            st.rerun()

if __name__ == "__main__":
    main()
