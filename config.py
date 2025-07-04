# Configuration settings for Excel AI Analyzer

# Application settings
APP_NAME = "Excel AI Analyzer"
APP_VERSION = "1.0.0"
DEBUG = False

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
