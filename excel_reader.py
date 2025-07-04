import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ExcelReader:
    """Class to handle Excel file reading and processing."""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls']
        
    def read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Read Excel file and return dictionary of DataFrames.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name to read (if None, reads all sheets)
            
        Returns:
            Dictionary with sheet names as keys and DataFrames as values
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                return {sheet_name: df}
            else:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path)
                sheets = {}
                for sheet in excel_file.sheet_names:
                    sheets[sheet] = pd.read_excel(file_path, sheet_name=sheet)
                return sheets
                
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise ValueError(f"Could not read Excel file: {str(e)}")
    
    def get_sheet_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about the Excel file structure.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with file information
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            info = {
                'file_path': file_path,
                'sheet_names': excel_file.sheet_names,
                'total_sheets': len(excel_file.sheet_names)
            }
            
            # Get info for each sheet
            sheet_details = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_details[sheet_name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.to_dict(),
                    'has_nulls': df.isnull().any().to_dict(),
                    'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
                }
            
            info['sheet_details'] = sheet_details
            return info
            
        except Exception as e:
            logger.error(f"Error getting sheet info: {str(e)}")
            raise ValueError(f"Could not get sheet information: {str(e)}")
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive summary of a DataFrame.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with data summary
        """
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }
        
        # Numeric columns statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            summary['numeric_stats'] = df[numeric_columns].describe().to_dict()
        
        # Categorical columns statistics
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            cat_stats = {}
            for col in categorical_columns:
                cat_stats[col] = {
                    'unique_values': df[col].nunique(),
                    'most_frequent': df[col].mode().iloc[0] if not df[col].empty else None,
                    'top_5_values': df[col].value_counts().head().to_dict()
                }
            summary['categorical_stats'] = cat_stats
        
        return summary
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if the file is a supported Excel format.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid Excel file, False otherwise
        """
        try:
            # Check file extension
            if not any(file_path.lower().endswith(fmt) for fmt in self.supported_formats):
                return False
            
            # Try to read the file
            pd.ExcelFile(file_path)
            return True
            
        except Exception:
            return False
    
    def clean_data(self, df: pd.DataFrame, 
                   remove_duplicates: bool = True,
                   handle_nulls: str = 'keep') -> pd.DataFrame:
        """
        Clean the DataFrame with basic preprocessing.
        
        Args:
            df: Input DataFrame
            remove_duplicates: Whether to remove duplicate rows
            handle_nulls: How to handle null values ('keep', 'drop', 'fill')
            
        Returns:
            Cleaned DataFrame
        """
        cleaned_df = df.copy()
        
        # Remove duplicates
        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()
        
        # Handle null values
        if handle_nulls == 'drop':
            cleaned_df = cleaned_df.dropna()
        elif handle_nulls == 'fill':
            # Fill numeric columns with median, categorical with mode
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype in ['int64', 'float64']:
                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                else:
                    mode_val = cleaned_df[col].mode()
                    if not mode_val.empty:
                        cleaned_df[col].fillna(mode_val.iloc[0], inplace=True)
        
        return cleaned_df
