#!/usr/bin/env python3
"""
Google Sheets Sample Data Generator

This script generates sample datasets directly in Google Sheets for testing
the Excel AI Analyzer's Google Sheets integration capabilities.

Usage:
    python create_google_sheets_sample.py
    
Requirements:
    - Google Cloud service account with Sheets API access
    - Credentials file or environment variable configured
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os
import sys
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheetsSampleGenerator:
    """Generate sample data in Google Sheets for testing."""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_dict: Optional[Dict] = None):
        """
        Initialize the Google Sheets sample generator.
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_dict: Service account credentials as dictionary
        """
        self.client = None
        self.credentials_path = credentials_path
        self.credentials_dict = credentials_dict
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
    def authenticate(self) -> bool:
        """Authenticate with Google Sheets API."""
        try:
            if self.credentials_dict:
                credentials = Credentials.from_service_account_info(
                    self.credentials_dict, scopes=self.scopes
                )
            elif self.credentials_path and os.path.exists(self.credentials_path):
                credentials = Credentials.from_service_account_file(
                    self.credentials_path, scopes=self.scopes
                )
            elif os.getenv('GOOGLE_SHEETS_CREDENTIALS'):
                # Try to load from environment variable
                creds_str = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
                credentials_dict = json.loads(creds_str)
                credentials = Credentials.from_service_account_info(
                    credentials_dict, scopes=self.scopes
                )
            else:
                logger.error("No Google Sheets credentials found")
                return False
                
            self.client = gspread.authorize(credentials)
            logger.info("✅ Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            return False
    
    def generate_sales_data(self, num_records: int = 1000) -> pd.DataFrame:
        """Generate sample sales data."""
        logger.info(f"📊 Generating {num_records} sales records...")
        
        # Product data
        products = [
            'Laptop Pro', 'Desktop Elite', 'Tablet Max', 'Phone Ultra',
            'Headphones Premium', 'Monitor 4K', 'Keyboard Wireless',
            'Mouse Gaming', 'Webcam HD', 'Speaker Bluetooth'
        ]
        
        categories = ['Electronics', 'Computers', 'Accessories', 'Mobile']
        regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa']
        sales_reps = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown']
        
        # Generate data
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_records):
            date = start_date + timedelta(days=random.randint(0, 365))
            product = random.choice(products)
            category = random.choice(categories)
            region = random.choice(regions)
            sales_rep = random.choice(sales_reps)
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(50, 2000), 2)
            total_sales = round(quantity * unit_price, 2)
            discount = round(random.uniform(0, 0.2), 3)
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Product': product,
                'Category': category,
                'Region': region,
                'Sales_Rep': sales_rep,
                'Quantity': quantity,
                'Unit_Price': unit_price,
                'Total_Sales': total_sales,
                'Discount': discount
            })
        
        return pd.DataFrame(data)
    
    def generate_employee_data(self, num_records: int = 500) -> pd.DataFrame:
        """Generate sample employee data."""
        logger.info(f"👥 Generating {num_records} employee records...")
        
        departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
        positions = {
            'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager'],
            'Sales': ['Sales Rep', 'Account Manager', 'Sales Director', 'VP Sales'],
            'Marketing': ['Marketing Specialist', 'Marketing Manager', 'Content Creator', 'CMO'],
            'HR': ['HR Specialist', 'HR Manager', 'Recruiter', 'CHRO'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'CFO'],
            'Operations': ['Operations Specialist', 'Operations Manager', 'Supply Chain', 'COO']
        }
        
        locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Berlin']
        
        data = []
        for i in range(num_records):
            emp_id = f"EMP{str(i+1).zfill(4)}"
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
            
            department = random.choice(departments)
            position = random.choice(positions[department])
            location = random.choice(locations)
            
            # Salary based on position level
            base_salary = {
                'Specialist': random.randint(50000, 80000),
                'Engineer': random.randint(70000, 120000),
                'Manager': random.randint(90000, 150000),
                'Director': random.randint(120000, 200000),
                'VP': random.randint(150000, 250000),
                'C-Level': random.randint(200000, 400000)
            }
            
            if 'Manager' in position or 'Lead' in position:
                salary = base_salary['Manager']
            elif 'Director' in position:
                salary = base_salary['Director']
            elif 'VP' in position or 'CMO' in position or 'CFO' in position or 'CHRO' in position or 'COO' in position:
                salary = base_salary['C-Level']
            elif 'Senior' in position:
                salary = base_salary['Engineer']
            else:
                salary = base_salary['Specialist']
                
            hire_date = datetime.now() - timedelta(days=random.randint(30, 2000))
            performance_score = round(random.uniform(3.0, 5.0), 1)
            
            data.append({
                'Employee_ID': emp_id,
                'First_Name': random.choice(first_names),
                'Last_Name': random.choice(last_names),
                'Department': department,
                'Position': position,
                'Location': location,
                'Hire_Date': hire_date.strftime('%Y-%m-%d'),
                'Salary': salary,
                'Performance_Score': performance_score,
                'Manager': f"{random.choice(first_names)} {random.choice(last_names)}",
                'Status': random.choice(['Active', 'Active', 'Active', 'Active', 'On Leave'])
            })
        
        return pd.DataFrame(data)
    
    def generate_inventory_data(self, num_records: int = 300) -> pd.DataFrame:
        """Generate sample inventory data."""
        logger.info(f"📦 Generating {num_records} inventory records...")
        
        categories = ['Electronics', 'Computers', 'Accessories', 'Software', 'Hardware']
        suppliers = ['TechCorp', 'ElectroSupply', 'CompuParts', 'GadgetWorld', 'TechDistrib']
        warehouses = ['Warehouse A', 'Warehouse B', 'Warehouse C', 'Distribution Center 1']
        
        data = []
        for i in range(num_records):
            product_id = f"PROD{str(i+1).zfill(4)}"
            product_names = [
                'Wireless Mouse', 'Bluetooth Keyboard', 'USB Cable', 'HDMI Adapter',
                'Power Bank', 'Phone Case', 'Screen Protector', 'Charging Dock',
                'Bluetooth Speaker', 'Wireless Earbuds', 'Phone Stand', 'Cable Organizer'
            ]
            
            category = random.choice(categories)
            supplier = random.choice(suppliers)
            warehouse = random.choice(warehouses)
            
            cost_price = round(random.uniform(5, 500), 2)
            selling_price = round(cost_price * random.uniform(1.2, 3.0), 2)
            stock_quantity = random.randint(0, 1000)
            reorder_level = random.randint(10, 100)
            
            last_restocked = datetime.now() - timedelta(days=random.randint(1, 90))
            
            data.append({
                'Product_ID': product_id,
                'Product_Name': random.choice(product_names),
                'Category': category,
                'Supplier': supplier,
                'Warehouse': warehouse,
                'Cost_Price': cost_price,
                'Selling_Price': selling_price,
                'Stock_Quantity': stock_quantity,
                'Reorder_Level': reorder_level,
                'Last_Restocked': last_restocked.strftime('%Y-%m-%d'),
                'Status': 'In Stock' if stock_quantity > reorder_level else 'Low Stock' if stock_quantity > 0 else 'Out of Stock'
            })
        
        return pd.DataFrame(data)
    
    def create_spreadsheet_with_data(self, title: str, sheets_data: Dict[str, pd.DataFrame]) -> Optional[str]:
        """
        Create a new Google Spreadsheet with multiple sheets of data.
        
        Args:
            title: The title of the spreadsheet
            sheets_data: Dictionary of sheet_name -> DataFrame
            
        Returns:
            URL of the created spreadsheet or None if failed
        """
        try:
            # Create new spreadsheet
            spreadsheet = self.client.create(title)
            logger.info(f"📋 Created spreadsheet: {title}")
            
            # Get the default sheet and rename it
            default_sheet = spreadsheet.sheet1
            first_sheet_name = list(sheets_data.keys())[0]
            default_sheet.update_title(first_sheet_name)
            
            # Add data to the first sheet
            first_df = sheets_data[first_sheet_name]
            self._populate_sheet(default_sheet, first_df)
            
            # Add remaining sheets
            for sheet_name, df in list(sheets_data.items())[1:]:
                new_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=len(df)+10, cols=len(df.columns)+5)
                self._populate_sheet(new_sheet, df)
            
            # Make spreadsheet shareable
            spreadsheet.share('', perm_type='anyone', role='reader')
            
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            logger.info(f"✅ Spreadsheet created successfully: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Failed to create spreadsheet: {str(e)}")
            return None
    
    def _populate_sheet(self, sheet, df: pd.DataFrame):
        """Populate a sheet with DataFrame data."""
        # Convert DataFrame to list of lists for batch update
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Update the sheet with data
        sheet.clear()
        sheet.update('A1', values)
        
        # Format headers
        sheet.format('1:1', {
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
        logger.info(f"📊 Populated sheet '{sheet.title}' with {len(df)} rows")
    
    def create_all_sample_sheets(self) -> Dict[str, str]:
        """Create all sample spreadsheets."""
        results = {}
        
        try:
            # Generate data
            sales_df = self.generate_sales_data(1000)
            employee_df = self.generate_employee_data(500)
            inventory_df = self.generate_inventory_data(300)
            
            # Create individual spreadsheets
            logger.info("🚀 Creating individual sample spreadsheets...")
            
            # Sales Data Spreadsheet
            sales_url = self.create_spreadsheet_with_data(
                "Excel AI - Sample Sales Data",
                {"Sales Data": sales_df}
            )
            if sales_url:
                results["Sales Data"] = sales_url
            
            # Employee Data Spreadsheet
            employee_url = self.create_spreadsheet_with_data(
                "Excel AI - Sample Employee Data", 
                {"Employee Data": employee_df}
            )
            if employee_url:
                results["Employee Data"] = employee_url
            
            # Inventory Data Spreadsheet
            inventory_url = self.create_spreadsheet_with_data(
                "Excel AI - Sample Inventory Data",
                {"Inventory Data": inventory_df}
            )
            if inventory_url:
                results["Inventory Data"] = inventory_url
            
            # Multi-sheet Demo Spreadsheet
            multi_url = self.create_spreadsheet_with_data(
                "Excel AI - Multi-Sheet Demo",
                {
                    "Sales": sales_df.head(100),
                    "Employees": employee_df.head(50),
                    "Inventory": inventory_df.head(30),
                    "Summary": pd.DataFrame({
                        'Dataset': ['Sales', 'Employees', 'Inventory'],
                        'Records': [100, 50, 30],
                        'Purpose': [
                            'Product sales analysis',
                            'HR analytics dataset',
                            'Stock management data'
                        ]
                    })
                }
            )
            if multi_url:
                results["Multi-Sheet Demo"] = multi_url
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to create sample sheets: {str(e)}")
            return results

def main():
    """Main function to run the Google Sheets sample generator."""
    print("🔗 Excel AI Analyzer - Google Sheets Sample Data Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = GoogleSheetsSampleGenerator()
    
    # Try to authenticate
    if not generator.authenticate():
        print("\n❌ Authentication failed!")
        print("\nTo use this script, you need:")
        print("1. Google Cloud service account with Sheets API access")
        print("2. Credentials JSON file or GOOGLE_SHEETS_CREDENTIALS environment variable")
        print("\nSetup instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Sheets API and Google Drive API")
        print("4. Create a service account")
        print("5. Download the JSON credentials file")
        print("6. Set GOOGLE_SHEETS_CREDENTIALS environment variable or")
        print("   place credentials.json in this directory")
        return
    
    print("\n🚀 Creating sample Google Sheets...")
    results = generator.create_all_sample_sheets()
    
    if results:
        print(f"\n✅ Successfully created {len(results)} sample spreadsheets:")
        print("=" * 60)
        for name, url in results.items():
            print(f"📊 {name}")
            print(f"   URL: {url}")
            print()
        
        print("🎉 Sample data generation complete!")
        print("\nYou can now use these URLs in the Excel AI Analyzer app")
        print("to test the Google Sheets integration.")
        
        # Save URLs to file for reference
        with open('sample_google_sheets_urls.txt', 'w') as f:
            f.write("Excel AI Analyzer - Sample Google Sheets URLs\n")
            f.write("=" * 50 + "\n\n")
            for name, url in results.items():
                f.write(f"{name}: {url}\n")
        
        print(f"\n📄 URLs saved to: sample_google_sheets_urls.txt")
        
    else:
        print("\n❌ No spreadsheets were created successfully.")
        print("Please check your credentials and try again.")

if __name__ == "__main__":
    main()
