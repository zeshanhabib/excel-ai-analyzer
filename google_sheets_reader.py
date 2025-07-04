import pandas as pd
import gspread
from google.auth.exceptions import GoogleAuthError
from google.oauth2.service_account import Credentials
import streamlit as st
import json
import os
from typing import Dict, List, Any, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)

class GoogleSheetsReader:
    """Class to handle Google Sheets reading and processing."""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_dict: Optional[Dict] = None):
        """
        Initialize Google Sheets reader.
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_dict: Service account credentials as dictionary
        """
        self.client = None
        self.credentials_path = credentials_path
        self.credentials_dict = credentials_dict
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if self.credentials_dict:
                # Use credentials dictionary (from Streamlit secrets or environment)
                credentials = Credentials.from_service_account_info(
                    self.credentials_dict, scopes=self.scopes
                )
            elif self.credentials_path and os.path.exists(self.credentials_path):
                # Use credentials file
                credentials = Credentials.from_service_account_file(
                    self.credentials_path, scopes=self.scopes
                )
            else:
                # Try to get from environment variable
                creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
                if creds_json:
                    credentials_dict = json.loads(creds_json)
                    credentials = Credentials.from_service_account_info(
                        credentials_dict, scopes=self.scopes
                    )
                else:
                    logger.error("No Google Sheets credentials found")
                    return False
            
            self.client = gspread.authorize(credentials)
            return True
            
        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {str(e)}")
            return False
    
    def extract_sheet_id(self, url: str) -> Optional[str]:
        """
        Extract Google Sheets ID from URL.
        
        Args:
            url: Google Sheets URL
            
        Returns:
            Sheet ID if found, None otherwise
        """
        # Pattern to match Google Sheets URLs
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just an ID
        if re.match(r'^[a-zA-Z0-9-_]+$', url):
            return url
            
        return None
    
    def read_google_sheet(self, 
                         sheet_url_or_id: str, 
                         worksheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Read Google Sheets data and return as DataFrame(s).
        
        Args:
            sheet_url_or_id: Google Sheets URL or ID
            worksheet_name: Specific worksheet name (if None, reads all worksheets)
            
        Returns:
            Dictionary with worksheet names as keys and DataFrames as values
        """
        if not self.client:
            if not self.authenticate():
                raise ValueError("Google Sheets authentication failed")
        
        try:
            # Extract sheet ID from URL
            sheet_id = self.extract_sheet_id(sheet_url_or_id)
            if not sheet_id:
                raise ValueError("Invalid Google Sheets URL or ID")
            
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(sheet_id)
            
            sheets_data = {}
            
            if worksheet_name:
                # Read specific worksheet
                try:
                    worksheet = spreadsheet.worksheet(worksheet_name)
                    data = worksheet.get_all_records()
                    df = pd.DataFrame(data)
                    sheets_data[worksheet_name] = df
                except gspread.WorksheetNotFound:
                    raise ValueError(f"Worksheet '{worksheet_name}' not found")
            else:
                # Read all worksheets
                worksheets = spreadsheet.worksheets()
                for worksheet in worksheets:
                    try:
                        data = worksheet.get_all_records()
                        if data:  # Only include non-empty worksheets
                            df = pd.DataFrame(data)
                            sheets_data[worksheet.title] = df
                    except Exception as e:
                        logger.warning(f"Could not read worksheet '{worksheet.title}': {str(e)}")
                        continue
            
            return sheets_data
            
        except GoogleAuthError as e:
            logger.error(f"Google authentication error: {str(e)}")
            raise ValueError("Google Sheets authentication failed. Check your credentials.")
        except Exception as e:
            logger.error(f"Error reading Google Sheets: {str(e)}")
            raise ValueError(f"Could not read Google Sheets: {str(e)}")
    
    def get_sheet_info(self, sheet_url_or_id: str) -> Dict[str, Any]:
        """
        Get information about the Google Sheets file.
        
        Args:
            sheet_url_or_id: Google Sheets URL or ID
            
        Returns:
            Dictionary with sheet information
        """
        if not self.client:
            if not self.authenticate():
                raise ValueError("Google Sheets authentication failed")
        
        try:
            sheet_id = self.extract_sheet_id(sheet_url_or_id)
            if not sheet_id:
                raise ValueError("Invalid Google Sheets URL or ID")
            
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheets = spreadsheet.worksheets()
            
            info = {
                'title': spreadsheet.title,
                'sheet_id': sheet_id,
                'url': spreadsheet.url,
                'worksheet_names': [ws.title for ws in worksheets],
                'total_worksheets': len(worksheets)
            }
            
            # Get details for each worksheet
            worksheet_details = {}
            for worksheet in worksheets:
                try:
                    data = worksheet.get_all_records()
                    if data:
                        df = pd.DataFrame(data)
                        worksheet_details[worksheet.title] = {
                            'rows': len(df),
                            'columns': len(df.columns),
                            'column_names': df.columns.tolist(),
                            'data_types': df.dtypes.to_dict(),
                            'has_nulls': df.isnull().any().to_dict(),
                        }
                    else:
                        worksheet_details[worksheet.title] = {
                            'rows': 0,
                            'columns': 0,
                            'column_names': [],
                            'note': 'Empty worksheet'
                        }
                except Exception as e:
                    worksheet_details[worksheet.title] = {
                        'error': f"Could not read worksheet: {str(e)}"
                    }
            
            info['worksheet_details'] = worksheet_details
            return info
            
        except Exception as e:
            logger.error(f"Error getting Google Sheets info: {str(e)}")
            raise ValueError(f"Could not get Google Sheets information: {str(e)}")
    
    def validate_access(self, sheet_url_or_id: str) -> bool:
        """
        Validate if we can access the Google Sheets file.
        
        Args:
            sheet_url_or_id: Google Sheets URL or ID
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return False
            
            sheet_id = self.extract_sheet_id(sheet_url_or_id)
            if not sheet_id:
                return False
            
            # Try to open the spreadsheet
            spreadsheet = self.client.open_by_key(sheet_id)
            return True
            
        except Exception:
            return False
    
    def get_available_worksheets(self, sheet_url_or_id: str) -> List[str]:
        """
        Get list of available worksheet names.
        
        Args:
            sheet_url_or_id: Google Sheets URL or ID
            
        Returns:
            List of worksheet names
        """
        try:
            if not self.client:
                if not self.authenticate():
                    return []
            
            sheet_id = self.extract_sheet_id(sheet_url_or_id)
            if not sheet_id:
                return []
            
            spreadsheet = self.client.open_by_key(sheet_id)
            return [ws.title for ws in spreadsheet.worksheets()]
            
        except Exception as e:
            logger.error(f"Error getting worksheets: {str(e)}")
            return []

class UnifiedDataReader:
    """Unified reader for both Excel files and Google Sheets."""
    
    def __init__(self, google_credentials_path: Optional[str] = None, 
                 google_credentials_dict: Optional[Dict] = None):
        """Initialize unified data reader."""
        from excel_reader import ExcelReader
        
        self.excel_reader = ExcelReader()
        self.google_reader = GoogleSheetsReader(
            credentials_path=google_credentials_path,
            credentials_dict=google_credentials_dict
        )
    
    def read_data(self, source: str, worksheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Read data from either Excel file or Google Sheets.
        
        Args:
            source: File path (for Excel) or URL/ID (for Google Sheets)
            worksheet_name: Specific worksheet/sheet name
            
        Returns:
            Dictionary with sheet names as keys and DataFrames as values
        """
        # Detect source type
        if self._is_google_sheets_url(source):
            return self.google_reader.read_google_sheet(source, worksheet_name)
        else:
            return self.excel_reader.read_excel(source, worksheet_name)
    
    def get_source_info(self, source: str) -> Dict[str, Any]:
        """Get information about the data source."""
        if self._is_google_sheets_url(source):
            return self.google_reader.get_sheet_info(source)
        else:
            return self.excel_reader.get_sheet_info(source)
    
    def validate_source(self, source: str) -> bool:
        """Validate if the source is accessible."""
        if self._is_google_sheets_url(source):
            return self.google_reader.validate_access(source)
        else:
            return self.excel_reader.validate_file(source)
    
    def _is_google_sheets_url(self, source: str) -> bool:
        """Check if source is a Google Sheets URL or ID."""
        google_patterns = [
            'docs.google.com/spreadsheets',
            'drive.google.com',
            '/spreadsheets/d/',
        ]
        
        return any(pattern in source for pattern in google_patterns) or \
               re.match(r'^[a-zA-Z0-9-_]{20,}$', source)  # Google Sheets ID pattern
