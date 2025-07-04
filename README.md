# 📊 Excel AI Analyzer

A powerful Python application that reads Excel sheets and performs comprehensive AI-powered analysis and queries. Trans### 4. **Ask Questions**
Examples of natural language queries:
- "What are the top 5 products by sales?"
- "Show me trends over time"
- "Find any anomalies in the data"
- "What's the correlation between price and sales?"
- "Which regions perform best?"
- "Are there any outliers I should know about?"

### 5. **Generate Sample Google Sheets**
If you have Google Sheets credentials configured:
- **Quick Testing**: Generate sample datasets directly in Google Sheets
- **Team Collaboration**: Share generated sheets with your team
- **Real-time Updates**: Test live data synchronization
- **Multiple Formats**: Sales, HR, Inventory, and Multi-sheet demos

### 6. **Get AI Insights**spreadsheet data into actionable insights with natural language processing and intelligent visualizations.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5+-green.svg)](https://openai.com)

## ✨ Features

### 📊 **Excel Processing**
- Read and parse Excel files (.xlsx, .xls)
- Multi-sheet support with automatic detection
- Data type inference and validation
- Comprehensive data quality assessment

### 🔗 **Google Sheets Integration**
- Direct Google Sheets URL support
- Real-time data access from shared sheets
- Service account authentication
- Multi-worksheet handling
- Sample data generation for Google Sheets
- Automatic sheet formatting and sharing

### 🤖 **AI-Powered Analysis**
- Natural language queries about your data
- Intelligent data insights and pattern recognition
- Anomaly detection with statistical methods
- Smart visualization recommendations
- Automated data profiling and suggestions

### 📈 **Interactive Visualizations**
- Automatic chart generation based on data types
- Correlation matrices and scatter plots
- Time series analysis
- Distribution plots and box plots
- Customizable interactive dashboards

### 🔍 **Data Quality Tools**
- Missing data analysis
- Duplicate detection
- Outlier identification
- Data type recommendations
- Cleaning suggestions

### 🐳 **Docker Support**
- Fully containerized application
- Docker Compose for easy deployment
- Optional reverse proxy with Traefik
- Production-ready configuration

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)
```bash
# 1. Clone the repository
git clone <repository-url>
cd excel_ai

# 2. Configure environment
cp .env.docker .env
# Edit .env with your API keys

# 3. Start with Docker
./docker-start.sh
# Access at http://localhost:8501
```

### Option 2: Docker with Custom Domain
```bash
# Start with reverse proxy (Traefik)
./docker-start.sh start-proxy
# Access at http://excel-ai.localhost
```

### Option 3: Local Development
```bash
# 1. Clone the repository
git clone <repository-url>
cd excel_ai

# 2. Run the startup script (handles everything)
./start.sh
```

### Option 4: Manual Setup
```bash
# 1. Clone the repository
git clone <repository-url>
cd excel_ai

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create sample data (optional)
python create_sample_data.py

# 5. Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys

# 6. Run the application
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # Optional: specify model
```

### OpenAI API Key
- Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- Add it to your `.env` file or enter it in the sidebar when running the app
- AI features will be disabled without an API key, but basic analysis still works

## 💡 Usage Guide

### 1. **Upload Your Data**
- Use the sidebar file uploader for Excel files
- Enter Google Sheets URL for direct access
- Use sample data for quick testing
- Generate sample Google Sheets (if credentials configured)

### 2. **Google Sheets Integration**
- **Upload Credentials**: Upload your service account JSON file
- **Enter Sheet URL**: Paste Google Sheets URL or ID
- **Generate Samples**: Create test datasets directly in Google Sheets
- **Real-time Access**: Changes in sheets are reflected immediately

### 3. **Explore Your Data**
- **Overview Tab**: Basic statistics and data quality assessment
- **AI Analysis Tab**: Get intelligent insights and ask questions
- **Visualizations Tab**: Interactive charts and graphs
- **Export Tab**: Download results and reports

### 4. **Ask Questions**
Examples of natural language queries:
- "What are the top 5 products by sales?"
- "Show me trends over time"
- "Find any anomalies in the data"
- "What's the correlation between price and sales?"
- "Which regions perform best?"
- "Are there any outliers I should know about?"

### 5. **Get AI Insights**
- Automatic data structure analysis
- Pattern recognition and trends
- Data quality recommendations
- Business insights and suggestions

## 📁 Project Structure

```
excel_ai/
├── 📱 app.py                    # Main Streamlit application
├── 📊 excel_reader.py           # Excel file processing and validation
├── 🔗 google_sheets_reader.py   # Google Sheets integration
├── 🤖 ai_analyzer.py            # AI analysis engine with OpenAI integration
├── 📈 visualizer.py             # Interactive data visualization
├── 🛠️ utils.py                 # Utility functions and data processing
├── ⚙️ config.py                # Configuration settings
├── 🧪 test_app.py              # Comprehensive test suite
├── 🏗️ create_sample_data.py    # Sample data generation (Excel & Google Sheets)
├── 📋 create_google_sheets_sample.py # Google Sheets sample data generator
├── 🚀 start.sh                 # Easy startup script
├── � docker-start.sh          # Docker deployment script
├── �📋 requirements.txt         # Python dependencies
├── 🐳 Dockerfile               # Docker container configuration
├── 🐳 docker-compose.yml       # Docker services orchestration
├── ⚙️ .env.example             # Environment variables template
├── ⚙️ .env.docker              # Docker environment template
├── 📁 sample_data/             # Sample Excel files for testing
│   ├── sales_data.xlsx
│   ├── employee_data.xlsx
│   ├── inventory_data.xlsx
│   └── multi_sheet_example.xlsx
└── 📖 README.md               # This file
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_app.py
```

This validates:
- ✅ Excel file reading and processing
- ✅ Data validation and type detection
- ✅ Visualization generation
- ✅ Utility functions
- ✅ Sample data integrity

## 📊 Sample Data

The project includes sample datasets for testing:

- **Sales Data** (1,000 records): Product sales with regions, dates, and revenue
- **Employee Data** (500 records): HR data with salaries, departments, and performance
- **Inventory Data** (300 records): Product inventory with stock levels and suppliers
- **Multi-sheet Example**: Combined sample data in multiple sheets

### 🔗 Google Sheets Sample Data

Generate sample data directly in Google Sheets for testing:

```bash
# Create sample Google Sheets with your credentials
python create_google_sheets_sample.py

# Or use the interactive generator in the app
# Go to sidebar → "Generate Sample Google Sheets"
```

**Sample Sheets Created:**
- **Sample Sales Data**: Product sales analysis
- **Sample Employee Data**: HR analytics dataset  
- **Sample Inventory Data**: Stock management data
- **Multi-Sheet Demo**: Combined datasets for testing

**Features:**
- Automatic sheet creation and formatting
- Shareable URLs for team collaboration
- Real-time data updates
- Professional formatting with headers

## 🔧 Advanced Features

### Custom Visualizations
- Build custom charts with the interactive chart builder
- Support for scatter plots, bar charts, line charts, and more
- Color coding and size mapping options

### Data Export
- Download processed data as CSV or Excel
- Generate comprehensive data profile reports
- Export visualizations as images

### Anomaly Detection
- Statistical outlier detection using IQR method
- AI-powered anomaly interpretation
- Visual highlighting of unusual patterns

## 🛠️ Dependencies

Key libraries used:
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **OpenAI**: AI-powered analysis
- **Plotly**: Interactive visualizations
- **Openpyxl**: Excel file processing
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning utilities

## ⚠️ Troubleshooting

### Common Issues

1. **"ImportError: No module named 'streamlit'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"OpenAI API Error"**
   - Check your API key in the `.env` file
   - Verify you have credits in your OpenAI account
   - The app works without AI features if no API key is provided

3. **"Excel file not reading"**
   - Ensure file is .xlsx or .xls format
   - Check if file is corrupted or password-protected
   - Try with the provided sample data first

4. **"Permission denied: start.sh"**
   ```bash
   chmod +x start.sh
   ```

5. **"Google Sheets authentication failed"**
   - Ensure your service account has proper permissions
   - Verify Google Sheets API and Drive API are enabled
   - Check that the credentials JSON file is valid
   - Make sure the sheet is shared with the service account email

6. **"Could not create Google Sheets sample"**
   - Verify your service account has write permissions
   - Check Google Drive API quota limits
   - Ensure sufficient storage space in Google Drive

### Google Sheets Setup Guide

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to IAM & Admin → Service Accounts
   - Create a new service account
   - Download the JSON credentials file

4. **Configure Permissions**
   - Share your Google Sheets with the service account email
   - Grant "Editor" or "Viewer" permissions as needed

### Performance Tips
- For large files (>50MB), consider filtering data first
- AI analysis works best with datasets under 10,000 rows
- Use data cleaning suggestions to improve performance

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional chart types
- More AI analysis features
- Support for other file formats (CSV, JSON)
- Enhanced data cleaning algorithms
- Custom AI model integration

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Use Cases

Perfect for:
- **Business Analysts**: Quick insights from Excel reports
- **Data Scientists**: Initial data exploration and profiling
- **Managers**: Understanding trends and patterns in business data
- **Researchers**: Analyzing survey and experimental data
- **Students**: Learning data analysis concepts

## 🔮 Future Enhancements

- Support for real-time data connections
- Advanced machine learning models
- Custom dashboard creation
- Collaborative features
- API endpoints for programmatic access

---

**Made with ❤️ for data enthusiasts everywhere!**

*Transform your spreadsheets into insights with the power of AI.*
