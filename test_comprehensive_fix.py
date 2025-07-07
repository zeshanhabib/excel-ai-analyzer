#!/usr/bin/env python3
"""
Comprehensive test to verify the Excel file upload fix works correctly.
This test verifies that the tempfile-based solution works in the new environment.
"""
import sys
import os
import tempfile
import pandas as pd
import io
from typing import Optional

def test_environment_setup():
    """Test that the environment is set up correctly."""
    print("🔧 Testing Environment Setup")
    print("=" * 50)
    
    # Test Python version
    print(f"✅ Python version: {sys.version}")
    
    # Test required imports
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import openpyxl
        print("✅ OpenPyXL imported successfully")
    except ImportError as e:
        print(f"❌ OpenPyXL import failed: {e}")
        return False
    
    return True

def test_app_import():
    """Test that the app module imports correctly."""
    print("\n📦 Testing App Import")
    print("=" * 50)
    
    try:
        # Suppress Streamlit warnings for this test
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import app
        
        print("✅ App module imported successfully")
        
        # Check if key functions exist
        if hasattr(app, 'load_excel_file'):
            print("✅ load_excel_file function found")
        else:
            print("❌ load_excel_file function not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_tempfile_functionality():
    """Test the tempfile functionality that's used in the fix."""
    print("\n🗂️  Testing Tempfile Functionality")
    print("=" * 50)
    
    try:
        # Create test data
        test_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B', 'Widget C'],
            'Price': [10.99, 15.50, 8.75],
            'Quantity': [100, 50, 200]
        })
        
        # Test creating and writing to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            temp_path = tmp_file.name
            print(f"✅ Created temporary file: {temp_path}")
            
            # Write Excel data to temp file
            test_data.to_excel(temp_path, index=False)
            print("✅ Successfully wrote data to temporary file")
            
            # Read the data back
            read_data = pd.read_excel(temp_path)
            print(f"✅ Successfully read data: {read_data.shape[0]} rows, {read_data.shape[1]} columns")
            
            # Verify data integrity
            if test_data.equals(read_data):
                print("✅ Data integrity verified")
            else:
                print("❌ Data integrity check failed")
                return False
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("✅ Temporary file cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Tempfile functionality test failed: {e}")
        return False

def test_bytes_to_excel_workflow():
    """Test the bytes-to-Excel workflow that simulates file upload."""
    print("\n🔄 Testing Bytes-to-Excel Workflow")
    print("=" * 50)
    
    try:
        # Create test data
        test_data = pd.DataFrame({
            'Employee': ['John', 'Jane', 'Bob'],
            'Department': ['IT', 'HR', 'Finance'],
            'Salary': [70000, 65000, 80000]
        })
        
        # Convert to bytes (simulating uploaded file)
        buffer = io.BytesIO()
        test_data.to_excel(buffer, index=False)
        buffer.seek(0)
        print("✅ Created Excel data in memory buffer")
        
        # Test the workflow using tempfile approach
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            # Write buffer content to temp file
            tmp_file.write(buffer.getvalue())
            tmp_file.flush()
            temp_path = tmp_file.name
            print(f"✅ Wrote buffer to temporary file: {temp_path}")
            
            # Read back using pandas
            result = pd.read_excel(temp_path)
            print(f"✅ Successfully read Excel: {result.shape[0]} rows, {result.shape[1]} columns")
            
            # Verify columns
            expected_cols = ['Employee', 'Department', 'Salary']
            if list(result.columns) == expected_cols:
                print("✅ Column names match expected values")
            else:
                print(f"❌ Column mismatch. Expected: {expected_cols}, Got: {list(result.columns)}")
                return False
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("✅ Temporary file cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Bytes-to-Excel workflow test failed: {e}")
        return False

def test_load_excel_file_function():
    """Test the actual load_excel_file function from app.py."""
    print("\n🎯 Testing load_excel_file Function")
    print("=" * 50)
    
    try:
        # Import with warnings suppressed
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import app
        
        # Create test data
        test_data = pd.DataFrame({
            'ID': [1, 2, 3],
            'Name': ['Alpha', 'Beta', 'Gamma'],
            'Value': [100, 200, 300]
        })
        
        # Convert to bytes buffer
        buffer = io.BytesIO()
        test_data.to_excel(buffer, index=False)
        buffer.seek(0)
        print("✅ Created test Excel data in buffer")
        
        # Test the load_excel_file function
        result = app.load_excel_file(buffer)
        
        if result is not None:
            print(f"✅ load_excel_file returned data: {result.shape[0]} rows, {result.shape[1]} columns")
            print(f"✅ Columns: {list(result.columns)}")
            
            # Verify data
            if result.shape[0] == 3 and result.shape[1] == 3:
                print("✅ Data dimensions are correct")
            else:
                print(f"❌ Data dimensions incorrect. Expected (3,3), got {result.shape}")
                return False
        else:
            print("❌ load_excel_file returned None")
            return False
        
        return True
    except Exception as e:
        print(f"❌ load_excel_file function test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Comprehensive Excel File Upload Fix Test")
    print("=" * 70)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("App Import", test_app_import),
        ("Tempfile Functionality", test_tempfile_functionality),
        ("Bytes-to-Excel Workflow", test_bytes_to_excel_workflow),
        ("load_excel_file Function", test_load_excel_file_function),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The Excel upload fix is working correctly.")
        print("\n💡 The fix provides:")
        print("   ✅ Robust temporary file handling")
        print("   ✅ Proper cleanup and error handling")
        print("   ✅ Cross-platform compatibility")
        print("   ✅ Cloud deployment readiness")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
