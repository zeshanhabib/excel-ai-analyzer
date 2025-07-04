import pandas as pd
import numpy as np
import io
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('excel_ai.log')
        ]
    )

def validate_dataframe(df: pd.DataFrame, min_rows: int = 1, min_cols: int = 1) -> Tuple[bool, str]:
    """
    Validate if DataFrame meets minimum requirements.
    
    Args:
        df: Pandas DataFrame to validate
        min_rows: Minimum number of rows required
        min_cols: Minimum number of columns required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None:
        return False, "DataFrame is None"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    if len(df) < min_rows:
        return False, f"DataFrame has {len(df)} rows, minimum {min_rows} required"
    
    if len(df.columns) < min_cols:
        return False, f"DataFrame has {len(df.columns)} columns, minimum {min_cols} required"
    
    return True, "DataFrame is valid"

def detect_column_types(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Detect and categorize column types with additional metadata.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary with column type information
    """
    column_info = {}
    
    for col in df.columns:
        col_data = df[col]
        dtype = str(col_data.dtype)
        
        info = {
            'dtype': dtype,
            'null_count': col_data.isnull().sum(),
            'null_percentage': (col_data.isnull().sum() / len(df)) * 100,
            'unique_count': col_data.nunique(),
            'unique_percentage': (col_data.nunique() / len(df)) * 100
        }
        
        # Determine semantic type
        if dtype in ['int64', 'float64']:
            info['semantic_type'] = 'numeric'
            info['min'] = col_data.min()
            info['max'] = col_data.max()
            info['mean'] = col_data.mean()
            info['median'] = col_data.median()
            info['std'] = col_data.std()
        elif dtype == 'object':
            # Check if it could be a date
            try:
                pd.to_datetime(col_data.dropna().head(100), errors='raise')
                info['semantic_type'] = 'date'
            except:
                # Check if it's categorical
                if info['unique_percentage'] < 50:  # Less than 50% unique values
                    info['semantic_type'] = 'categorical'
                    info['top_values'] = col_data.value_counts().head(5).to_dict()
                else:
                    info['semantic_type'] = 'text'
        elif 'datetime' in dtype:
            info['semantic_type'] = 'date'
            info['date_range'] = {
                'start': col_data.min(),
                'end': col_data.max()
            }
        else:
            info['semantic_type'] = 'other'
        
        column_info[col] = info
    
    return column_info

def suggest_data_cleaning(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Suggest data cleaning operations based on data quality analysis.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        List of cleaning suggestions
    """
    suggestions = []
    column_info = detect_column_types(df)
    
    # Check for high null percentages
    for col, info in column_info.items():
        if info['null_percentage'] > 50:
            suggestions.append({
                'type': 'high_nulls',
                'column': col,
                'issue': f"Column has {info['null_percentage']:.1f}% missing values",
                'suggestion': "Consider dropping this column or investigating data source"
            })
        elif info['null_percentage'] > 10:
            suggestions.append({
                'type': 'moderate_nulls',
                'column': col,
                'issue': f"Column has {info['null_percentage']:.1f}% missing values",
                'suggestion': "Consider imputation or filling missing values"
            })
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        suggestions.append({
            'type': 'duplicates',
            'issue': f"Dataset contains {duplicate_count} duplicate rows",
            'suggestion': "Consider removing duplicate rows"
        })
    
    # Check for columns with single unique value
    for col, info in column_info.items():
        if info['unique_count'] == 1:
            suggestions.append({
                'type': 'constant_column',
                'column': col,
                'issue': "Column has only one unique value",
                'suggestion': "Consider dropping this column as it provides no information"
            })
    
    # Check for potential date columns stored as text
    for col, info in column_info.items():
        if info['semantic_type'] == 'text' and any(keyword in col.lower() 
                                                  for keyword in ['date', 'time', 'created', 'updated']):
            suggestions.append({
                'type': 'potential_date',
                'column': col,
                'issue': "Column name suggests it might contain dates",
                'suggestion': "Try converting to datetime format"
            })
    
    return suggestions

def format_number(number: Union[int, float], decimal_places: int = 2) -> str:
    """
    Format numbers for display with appropriate units.
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted string
    """
    if pd.isna(number):
        return "N/A"
    
    if abs(number) >= 1e9:
        return f"{number/1e9:.{decimal_places}f}B"
    elif abs(number) >= 1e6:
        return f"{number/1e6:.{decimal_places}f}M"
    elif abs(number) >= 1e3:
        return f"{number/1e3:.{decimal_places}f}K"
    else:
        return f"{number:.{decimal_places}f}"

def create_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create comprehensive summary statistics for a DataFrame.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary with summary statistics
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    summary = {
        'basic_info': {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'missing_values_total': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum()
        },
        'column_types': {
            'numeric': len(numeric_cols),
            'categorical': len(categorical_cols),
            'datetime': len(df.select_dtypes(include=['datetime']).columns)
        }
    }
    
    # Numeric summary
    if len(numeric_cols) > 0:
        summary['numeric_summary'] = {
            'columns': list(numeric_cols),
            'stats': df[numeric_cols].describe().to_dict()
        }
    
    # Categorical summary
    if len(categorical_cols) > 0:
        cat_summary = {}
        for col in categorical_cols:
            cat_summary[col] = {
                'unique_values': df[col].nunique(),
                'most_frequent': df[col].mode().iloc[0] if not df[col].empty else None,
                'top_5': df[col].value_counts().head().to_dict()
            }
        summary['categorical_summary'] = cat_summary
    
    return summary

def export_to_excel(df: pd.DataFrame, filename: str, sheet_name: str = "Data") -> str:
    """
    Export DataFrame to Excel file.
    
    Args:
        df: Pandas DataFrame
        filename: Output filename
        sheet_name: Excel sheet name
        
    Returns:
        Success message or error
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        return f"Data exported successfully to {filename}"
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        return f"Export failed: {str(e)}"

def create_data_profile_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a comprehensive data profiling report.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary with profiling information
    """
    column_info = detect_column_types(df)
    cleaning_suggestions = suggest_data_cleaning(df)
    summary_stats = create_summary_stats(df)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'dataset_info': {
            'shape': df.shape,
            'columns': list(df.columns),
            'size_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        },
        'column_analysis': column_info,
        'data_quality': {
            'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100,
            'completeness_score': 100 - ((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
        },
        'cleaning_suggestions': cleaning_suggestions,
        'summary_statistics': summary_stats
    }
    
    return report

def safe_column_selection(df: pd.DataFrame, columns: List[str]) -> List[str]:
    """
    Safely select columns that exist in the DataFrame.
    
    Args:
        df: Pandas DataFrame
        columns: List of column names to select
        
    Returns:
        List of valid column names
    """
    return [col for col in columns if col in df.columns]

def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """
    Detect outliers using the IQR method.
    
    Args:
        series: Pandas Series (numeric)
        multiplier: IQR multiplier for outlier detection
        
    Returns:
        Boolean Series indicating outliers
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (series < lower_bound) | (series > upper_bound)

def auto_detect_separators(file_path: str) -> str:
    """
    Auto-detect CSV separator if file is a CSV.
    
    Args:
        file_path: Path to file
        
    Returns:
        Detected separator or default comma
    """
    if not file_path.lower().endswith('.csv'):
        return ','
    
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline()
            
        # Common separators to test
        separators = [',', ';', '\t', '|']
        separator_counts = {}
        
        for sep in separators:
            separator_counts[sep] = first_line.count(sep)
        
        # Return separator with highest count
        return max(separator_counts, key=separator_counts.get)
        
    except Exception:
        return ','

def generate_insights_prompt(df: pd.DataFrame, user_question: str = "") -> str:
    """
    Generate a comprehensive prompt for AI analysis.
    
    Args:
        df: Pandas DataFrame
        user_question: Specific user question
        
    Returns:
        Formatted prompt string
    """
    column_info = detect_column_types(df)
    summary = create_summary_stats(df)
    
    prompt = f"""
    Analyze this dataset and provide insights:
    
    Dataset Overview:
    - Shape: {df.shape[0]} rows, {df.shape[1]} columns
    - Memory usage: {summary['basic_info']['memory_usage_mb']:.2f} MB
    - Missing values: {summary['basic_info']['missing_values_total']} total
    
    Column Information:
    """
    
    for col, info in column_info.items():
        prompt += f"\n- {col}: {info['semantic_type']} ({info['dtype']}) - {info['null_percentage']:.1f}% missing"
    
    if user_question:
        prompt += f"\n\nSpecific Question: {user_question}"
    
    prompt += """
    
    Please provide:
    1. Key insights about the data
    2. Notable patterns or trends
    3. Data quality assessment
    4. Actionable recommendations
    5. Potential business implications
    """
    
    return prompt
