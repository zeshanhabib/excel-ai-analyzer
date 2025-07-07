#!/usr/bin/env python3
"""
Test script to verify 99% accuracy improvements in Excel upload and processing pipeline.
Tests various Excel file scenarios and edge cases to ensure robust handling.
"""

import pandas as pd
import numpy as np
import tempfile
import os
import sys
from datetime import datetime, timedelta
import logging

# Add the project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import load_excel_file, _calculate_data_quality_score
from excel_reader import ExcelReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockUploadedFile:
    """Mock uploaded file for testing."""
    def __init__(self, file_path: str, name: str):
        with open(file_path, 'rb') as f:
            self._content = f.read()
        self.name = name
        self.size = len(self._content)
    
    def getbuffer(self):
        return self._content

def create_test_excel_files():
    """Create various test Excel files to test accuracy."""
    test_files = {}
    
    # Test 1: Clean, well-formatted data
    df_clean = pd.DataFrame({
        'Product_ID': range(1, 101),
        'Product_Name': [f'Product_{i}' for i in range(1, 101)],
        'Price': np.random.uniform(10, 1000, 100).round(2),
        'Quantity': np.random.randint(1, 100, 100),
        'Date_Added': pd.date_range('2023-01-01', periods=100, freq='D')
    })
    
    clean_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df_clean.to_excel(clean_file.name, index=False)
    test_files['clean_data'] = clean_file.name
    
    # Test 2: Data with headers in first row but messy formatting
    df_messy = pd.DataFrame({
        'Product ID ': [f'PROD-{i:03d}' for i in range(1, 51)],
        ' Price ($) ': [f'${x:.2f}' for x in np.random.uniform(10, 1000, 50)],
        'Quantity Available': np.random.randint(0, 100, 50),
        'Last Updated': pd.date_range('2023-01-01', periods=50, freq='W').strftime('%m/%d/%Y'),
        'Status ': np.random.choice(['Active', 'Inactive', '', 'Active '], 50)
    })
    
    messy_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df_messy.to_excel(messy_file.name, index=False)
    test_files['messy_data'] = messy_file.name
    
    # Test 3: Data with missing headers (data starts from first row)
    df_no_headers = pd.DataFrame([
        [1, 'Item A', 25.50, '2023-01-15', 'Available'],
        [2, 'Item B', 45.00, '2023-01-16', 'Out of Stock'],
        [3, 'Item C', 15.75, '2023-01-17', 'Available'],
        ['', 'Item D', 35.25, '2023-01-18', ''],
        [5, '', 55.00, '2023-01-19', 'Available']
    ])
    
    no_headers_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df_no_headers.to_excel(no_headers_file.name, index=False, header=False)
    test_files['no_headers'] = no_headers_file.name
    
    # Test 4: Multi-sheet file
    multi_sheet_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    with pd.ExcelWriter(multi_sheet_file.name) as writer:
        df_clean.to_excel(writer, sheet_name='Products', index=False)
        
        df_sales = pd.DataFrame({
            'Sale_ID': range(1, 201),
            'Product_ID': np.random.randint(1, 101, 200),
            'Sale_Amount': np.random.uniform(100, 5000, 200).round(2),
            'Sale_Date': pd.date_range('2023-01-01', periods=200, freq='H')
        })
        df_sales.to_excel(writer, sheet_name='Sales', index=False)
        
        # Empty sheet to test handling
        pd.DataFrame().to_excel(writer, sheet_name='Empty', index=False)
    
    test_files['multi_sheet'] = multi_sheet_file.name
    
    # Test 5: Data with various data type challenges
    df_types = pd.DataFrame({
        'Mixed_Numbers': ['123', '45.67', '$1,234.56', '89%', '1.23e-4', 'N/A'],
        'Mixed_Dates': ['2023-01-01', '01/15/2023', 'Jan 20, 2023', '2023-02-15 14:30:00', '', 'Invalid'],
        'Text_Data': ['  Clean Text  ', '', None, 'UPPERCASE', 'lowercase', '   '],
        'Boolean_Like': ['Yes', 'No', 'TRUE', 'FALSE', '1', '0'],
        'Percentages': ['10%', '25.5%', '100%', '0%', '', '150%']
    })
    
    types_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df_types.to_excel(types_file.name, index=False)
    test_files['data_types'] = types_file.name
    
    return test_files

def test_accuracy_scenario(file_path: str, file_name: str, scenario_name: str):
    """Test a specific accuracy scenario."""
    logger.info(f"\\nTesting scenario: {scenario_name}")
    logger.info(f"File: {file_name}")
    
    try:
        # Create mock uploaded file
        mock_file = MockUploadedFile(file_path, file_name)
        
        # Test the load_excel_file function
        result_df = load_excel_file(mock_file)
        
        if result_df is None:
            logger.error(f"❌ Failed to load file: {scenario_name}")
            return False
        
        # Validate the result
        if result_df.empty:
            logger.error(f"❌ Loaded DataFrame is empty: {scenario_name}")
            return False
        
        # Calculate quality score
        quality_score = _calculate_data_quality_score(result_df)
        
        logger.info(f"✅ Successfully loaded: {len(result_df)} rows, {len(result_df.columns)} columns")
        logger.info(f"📊 Data quality score: {quality_score:.1%}")
        
        # Additional validations
        validation_results = []
        
        # Check for proper column names
        has_proper_columns = all(isinstance(col, str) and col.strip() for col in result_df.columns)
        validation_results.append(("Proper column names", has_proper_columns))
        
        # Check for data type optimization
        numeric_cols = len(result_df.select_dtypes(include=[np.number]).columns)
        datetime_cols = len(result_df.select_dtypes(include=['datetime64']).columns)
        optimization_score = (numeric_cols + datetime_cols) / len(result_df.columns) if len(result_df.columns) > 0 else 0
        validation_results.append(("Data type optimization", optimization_score > 0.3))
        
        # Check for duplicate handling
        has_duplicates = result_df.duplicated().any()
        validation_results.append(("No duplicates", not has_duplicates))
        
        # Check overall quality threshold
        meets_quality_threshold = quality_score >= 0.90  # 90% quality threshold
        validation_results.append(("Quality threshold (90%+)", meets_quality_threshold))
        
        # Display validation results
        for check_name, passed in validation_results:
            status = "✅" if passed else "⚠️"
            logger.info(f"  {status} {check_name}: {'PASS' if passed else 'REVIEW'}")
        
        # Overall success criteria
        success = all(result[1] for result in validation_results)
        
        if success:
            logger.info(f"🎯 Scenario {scenario_name}: SUCCESS - High accuracy achieved!")
        else:
            logger.info(f"📈 Scenario {scenario_name}: GOOD - Some areas for improvement")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Exception in {scenario_name}: {str(e)}")
        return False

def run_comprehensive_accuracy_test():
    """Run comprehensive accuracy tests."""
    logger.info("🚀 Starting comprehensive Excel accuracy testing...")
    logger.info("=" * 60)
    
    # Create test files
    test_files = create_test_excel_files()
    
    test_scenarios = [
        ('clean_data', 'clean_products.xlsx', 'Clean Well-Formatted Data'),
        ('messy_data', 'messy_products.xlsx', 'Messy Formatting with Headers'),
        ('no_headers', 'data_no_headers.xlsx', 'Data Without Headers'),
        ('multi_sheet', 'multi_sheet.xlsx', 'Multi-Sheet Workbook'),
        ('data_types', 'mixed_types.xlsx', 'Mixed Data Types Challenge')
    ]
    
    results = []
    for file_key, file_name, scenario_name in test_scenarios:
        file_path = test_files[file_key]
        success = test_accuracy_scenario(file_path, file_name, scenario_name)
        results.append((scenario_name, success))
    
    # Summary
    logger.info("\\n" + "=" * 60)
    logger.info("📊 ACCURACY TEST SUMMARY")
    logger.info("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    accuracy_percentage = (passed_tests / total_tests) * 100
    
    for scenario_name, success in results:
        status = "✅ PASS" if success else "⚠️  REVIEW"
        logger.info(f"  {status} {scenario_name}")
    
    logger.info(f"\\n🎯 Overall Accuracy: {passed_tests}/{total_tests} tests passed ({accuracy_percentage:.1f}%)")
    
    if accuracy_percentage >= 99:
        logger.info("🏆 EXCELLENT: 99%+ accuracy target achieved!")
    elif accuracy_percentage >= 95:
        logger.info("🥇 GREAT: 95%+ accuracy achieved!")
    elif accuracy_percentage >= 90:
        logger.info("🥈 GOOD: 90%+ accuracy achieved!")
    else:
        logger.info("🔧 NEEDS IMPROVEMENT: Below 90% accuracy")
    
    # Cleanup
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except OSError:
            pass
    
    return accuracy_percentage >= 99

if __name__ == "__main__":
    success = run_comprehensive_accuracy_test()
    sys.exit(0 if success else 1)
