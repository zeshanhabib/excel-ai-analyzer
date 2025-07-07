# Configuration settings for Excel AI Analyzer

# Application settings
APP_NAME = "Excel AI Analyzer"
APP_VERSION = "1.0.0"
DEBUG = False

# Enhanced debugging options
DEBUG_LEVELS = {
    'MINIMAL': 0,      # Only basic info
    'STANDARD': 1,     # Include data flow info
    'DETAILED': 2,     # Include AI prompt/response sizes
    'FULL': 3          # Include complete data samples and AI prompts
}

# Current debug level (can be overridden by environment variable)
DEBUG_LEVEL = DEBUG_LEVELS['STANDARD']

# Debug data tracking settings
DEBUG_TRACK_DATA_SIZE = True           # Track data sizes at each step
DEBUG_TRACK_AI_PROMPTS = True          # Track AI prompt construction
DEBUG_TRACK_RESPONSE_QUALITY = True    # Track AI response quality metrics
DEBUG_SAVE_DEBUG_LOGS = True           # Save detailed debug logs to file
DEBUG_SHOW_DATA_SAMPLES = True         # Show data samples in debug output

# Data processing settings for AI analysis
AI_MAX_SAMPLE_ROWS = None              # None means use all data (was previously limited)
AI_USE_FULL_DATASET = True             # Ensure AI gets complete dataset info
AI_INCLUDE_DETAILED_STATS = True       # Include comprehensive statistics
AI_MAX_CONTEXT_LENGTH = 100000         # Maximum characters in AI context (increased for large datasets)
AI_SMART_SAMPLING_RATIO = 0.8          # Use 80% of available context for data representation

# Streamlit settings
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"

# File upload settings
MAX_FILE_SIZE_MB = 100
SUPPORTED_FORMATS = ['.xlsx', '.xls']

# AI settings
DEFAULT_AI_MODEL = "gpt-3.5-turbo"
MAX_AI_TOKENS = 1000
AI_TEMPERATURE = 0.3

# Visualization settings
DEFAULT_CHART_THEME = "plotly_white"
MAX_CHART_COLUMNS = 10

# Data processing settings
MAX_ROWS_PREVIEW = 1000
OUTLIER_IQR_MULTIPLIER = 1.5

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "excel_ai.log"
DEBUG_LOG_FILE = "excel_ai_debug.log"
