#!/usr/bin/env python3
"""
Test script for Excel AI Analyzer
Tests core functionality without requiring Streamlit or OpenAI API
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from excel_reader import ExcelReader
from visualizer import DataVisualizer
from utils import (
    validate_dataframe, detect_column_types, suggest_data_cleaning,
    create_data_profile_report, format_number
)

def test_excel_reader():
    """Test Excel reading functionality."""
    print("🧪 Testing Excel Reader...")
    
    reader = ExcelReader()
    
    # Test with sample data
    try:
        sheets = reader.read_excel("sample_data/sales_data.xlsx")
        print(f"✅ Successfully read Excel file with {len(sheets)} sheet(s)")
        
        # Test sheet info
        info = reader.get_sheet_info("sample_data/sales_data.xlsx")
        print(f"✅ Sheet info: {info['total_sheets']} sheets, {list(info['sheet_names'])}")
        
        # Test data summary
        df = list(sheets.values())[0]
        summary = reader.get_data_summary(df)
        print(f"✅ Data summary: {summary['shape']} shape, {len(summary['columns'])} columns")
        
        return True
    except Exception as e:
        print(f"❌ Excel reader test failed: {str(e)}")
        return False

def test_data_validation():
    """Test data validation utilities."""
    print("\n🧪 Testing Data Validation...")
    
    # Create test data
    df = pd.DataFrame({
        'A': [1, 2, 3, None, 5],
        'B': ['x', 'y', 'z', 'x', 'y'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5],
        'D': pd.date_range('2023-01-01', periods=5)
    })
    
    try:
        # Test validation
        is_valid, msg = validate_dataframe(df)
        print(f"✅ DataFrame validation: {is_valid} - {msg}")
        
        # Test column type detection
        column_info = detect_column_types(df)
        print(f"✅ Column types detected: {len(column_info)} columns analyzed")
        
        # Test cleaning suggestions
        suggestions = suggest_data_cleaning(df)
        print(f"✅ Cleaning suggestions: {len(suggestions)} suggestions generated")
        
        # Test data profile report
        report = create_data_profile_report(df)
        print(f"✅ Profile report generated with {len(report)} sections")
        
        return True
    except Exception as e:
        print(f"❌ Data validation test failed: {str(e)}")
        return False

def test_visualizer():
    """Test visualization functionality."""
    print("\n🧪 Testing Data Visualizer...")
    
    # Create test data
    np.random.seed(42)
    df = pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'value': np.random.randint(1, 100, 100),
        'date': pd.date_range('2023-01-01', periods=100)
    })
    
    visualizer = DataVisualizer()
    
    try:
        # Test correlation matrix
        fig = visualizer.create_correlation_matrix(df)
        print("✅ Correlation matrix created")
        
        # Test scatter plot
        fig = visualizer.create_scatter_plot(df, 'x', 'y', 'category')
        print("✅ Scatter plot created")
        
        # Test bar chart
        fig = visualizer.create_bar_chart(df, 'category', 'value')
        print("✅ Bar chart created")
        
        # Test overview dashboard
        fig = visualizer.create_overview_dashboard(df)
        print("✅ Overview dashboard created")
        
        # Test suggestions
        suggestions = visualizer.suggest_best_visualizations(df)
        print(f"✅ Visualization suggestions: {len(suggestions)} suggestions")
        
        return True
    except Exception as e:
        print(f"❌ Visualizer test failed: {str(e)}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\n🧪 Testing Utilities...")
    
    try:
        # Test number formatting
        assert format_number(1234.56) == "1.23K"
        assert format_number(1234567) == "1.23M"
        assert format_number(1234567890) == "1.23B"
        print("✅ Number formatting works correctly")
        
        # Test with real data
        df = pd.read_excel("sample_data/sales_data.xlsx")
        
        # Test column type detection
        column_info = detect_column_types(df)
        print(f"✅ Real data analysis: {len(column_info)} columns analyzed")
        
        return True
    except Exception as e:
        print(f"❌ Utilities test failed: {str(e)}")
        return False

def test_sample_data():
    """Test that sample data files exist and are readable."""
    print("\n🧪 Testing Sample Data...")
    
    sample_files = [
        "sample_data/sales_data.xlsx",
        "sample_data/employee_data.xlsx", 
        "sample_data/inventory_data.xlsx",
        "sample_data/multi_sheet_example.xlsx"
    ]
    
    success_count = 0
    
    for file_path in sample_files:
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                print(f"✅ {file_path}: {df.shape} - readable")
                success_count += 1
            else:
                print(f"❌ {file_path}: file not found")
        except Exception as e:
            print(f"❌ {file_path}: error reading - {str(e)}")
    
    return success_count == len(sample_files)

def main():
    """Run all tests."""
    print("🚀 Starting Excel AI Analyzer Tests...\n")
    
    tests = [
        ("Sample Data", test_sample_data),
        ("Excel Reader", test_excel_reader),
        ("Data Validation", test_data_validation),
        ("Visualizer", test_visualizer),
        ("Utilities", test_utilities)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED\n")
            else:
                print(f"❌ {test_name} test FAILED\n")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {str(e)}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\n🚀 To start the application, run:")
        print("streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
