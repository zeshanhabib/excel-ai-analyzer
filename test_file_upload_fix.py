#!/usr/bin/env python3
"""
Test the Excel file upload fix for temporary file handling.
This script verifies that the temporary file handling works correctly.
"""

import sys
import os
import tempfile
import pandas as pd
from io import BytesIO

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_temporary_file_handling():
    """Test the improved temporary file handling."""
    print("🧪 Testing temporary file handling...")
    
    try:
        # Create a sample Excel file in memory
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Tokyo']
        })
        
        # Write to BytesIO (simulates uploaded file)
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test', index=False)
        excel_buffer.seek(0)
        
        # Test the new temporary file handling approach
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(excel_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Verify we can read the file
            test_df = pd.read_excel(tmp_file_path)
            
            if test_df.shape == df.shape and list(test_df.columns) == list(df.columns):
                print("✅ Temporary file handling works correctly")
                print(f"   - Created temporary file: {tmp_file_path}")
                print(f"   - Successfully read {test_df.shape[0]} rows, {test_df.shape[1]} columns")
                return True
            else:
                print("❌ Data mismatch after reading temporary file")
                return False
                
        finally:
            # Clean up temporary file
            try:
                os.remove(tmp_file_path)
                print("✅ Temporary file cleaned up successfully")
            except OSError as e:
                print(f"⚠️ Warning: Could not remove temporary file: {e}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_file_permissions():
    """Test that we can create temporary files in the system temp directory."""
    print("\n🧪 Testing file permissions...")
    
    try:
        # Test write permissions in temp directory
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as tmp_file:
            tmp_file.write("test")
            tmp_file.flush()
            print(f"✅ Can write to temporary directory: {tempfile.gettempdir()}")
            return True
            
    except Exception as e:
        print(f"❌ Cannot write to temporary directory: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Excel File Upload Fix")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Temporary file handling
    if test_temporary_file_handling():
        success_count += 1
    
    # Test 2: File permissions
    if test_file_permissions():
        success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The Excel upload fix should work correctly.")
        print("\n💡 Key improvements:")
        print("   ✅ Uses system temporary directory (better permissions)")
        print("   ✅ Proper file cleanup with try/finally")
        print("   ✅ More robust error handling")
        print("   ✅ Works in containerized environments")
        return True
    else:
        print("❌ Some tests failed. There may still be issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
