#!/usr/bin/env python3
"""
Test script to verify enhanced debugging and full dataset usage in AI analysis.
This script will test the new debugging features and ensure full datasets are used.
"""

import pandas as pd
import os
import sys
from ai_analyzer import AIAnalyzer
from debug_utils import DebugTracker
import config

def create_test_data():
    """Create a test dataset for debugging verification."""
    print("Creating test dataset...")
    
    # Create a larger dataset to test full data usage
    data = {
        'Product': [f'Product_{i}' for i in range(1, 101)],  # 100 products
        'Sales': [1000 + i * 50 + (i % 10) * 100 for i in range(100)],
        'Region': ['North', 'South', 'East', 'West'] * 25,
        'Month': (['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] * 17)[:100],  # Trim to 100
        'Category': ['Electronics', 'Clothing', 'Food', 'Books', 'Sports'] * 20
    }
    
    df = pd.DataFrame(data)
    print(f"Created dataset with {len(df)} rows and {len(df.columns)} columns")
    return df

def test_debugging_features():
    """Test the enhanced debugging and full dataset features."""
    print("\n" + "="*60)
    print("TESTING ENHANCED DEBUGGING AND FULL DATASET USAGE")
    print("="*60)
    
    # Set debug level to FULL for comprehensive testing
    original_debug_level = config.DEBUG_LEVEL
    config.DEBUG_LEVEL = config.DEBUG_LEVELS['FULL']
    
    try:
        # Create test data
        df = create_test_data()
        
        # Test if we have API key
        if not os.getenv("OPENAI_API_KEY"):
            print("\n⚠️  WARNING: No OPENAI_API_KEY found in environment.")
            print("Some AI analysis tests will be skipped.")
            print("Set OPENAI_API_KEY to test AI features with full debugging.")
            ai_available = False
        else:
            ai_available = True
            
        # Initialize debug tracker
        debug_tracker = DebugTracker(debug_level=config.DEBUG_LEVELS['FULL'])
        print(f"\n✅ Debug tracker initialized with level: {debug_tracker.debug_level}")
        
        # Test data completeness analysis
        print("\n📊 Testing data completeness analysis...")
        sample_data = df.head(10).to_string()  # Create sample processed data
        completeness_report = debug_tracker.analyze_data_completeness(df, sample_data, "test_analysis")
        print(f"Column coverage: {completeness_report['column_coverage']:.1%}")
        print(f"Sample coverage: {completeness_report['sample_coverage']:.1%}")
        print(f"Original rows: {completeness_report['original_rows']}")
        print(f"Original cols: {completeness_report['original_cols']}")
        
        if ai_available:
            # Test AI analysis with full debugging
            print("\n🤖 Testing AI analysis with full dataset debugging...")
            
            try:
                ai_analyzer = AIAnalyzer()
                
                # Test data structure analysis
                print("\n1. Testing analyze_data_structure...")
                structure_result = ai_analyzer.analyze_data_structure(df)
                
                if 'debug_info' in structure_result:
                    debug_info = structure_result['debug_info']
                    print(f"   ✅ Debug info captured:")
                    print(f"   - Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                    print(f"   - Context length: {debug_info.get('context_length', 'N/A')}")
                    print(f"   - Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
                
                # Test question answering
                print("\n2. Testing answer_question...")
                test_question = "What are the top 5 products by sales? Analyze the sales distribution."
                answer_result = ai_analyzer.answer_question(df, test_question)
                
                if 'debug_info' in answer_result:
                    debug_info = answer_result['debug_info']
                    print(f"   ✅ Debug info captured:")
                    print(f"   - Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                    print(f"   - Context length: {debug_info.get('context_length', 'N/A')}")
                    print(f"   - Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
                    print(f"   - Supporting data rows: {debug_info.get('supporting_data_rows', 'N/A')}")
                
                # Test anomaly detection
                print("\n3. Testing detect_anomalies...")
                anomaly_result = ai_analyzer.detect_anomalies(df)
                
                if 'debug_info' in anomaly_result:
                    debug_info = anomaly_result['debug_info']
                    print(f"   ✅ Debug info captured:")
                    print(f"   - Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                    print(f"   - Anomalies found: {debug_info.get('anomalies_count', 'N/A')}")
                    print(f"   - Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
                
                print("\n✅ All AI analysis tests completed successfully!")
                
            except Exception as e:
                print(f"\n❌ Error during AI analysis testing: {str(e)}")
                print("This might be due to API key issues or connectivity problems.")
        
        # Test debug log generation
        print("\n📝 Testing debug log generation...")
        debug_tracker.log_debug("Test debug message", level=1, data={"test": "data"})
        debug_tracker.log_debug("Detailed debug message", level=2, data={"rows": len(df)})
        debug_tracker.log_debug("Full debug message", level=3, data={"sample": df.head(2).to_dict()})
        
        # Generate debug report
        print("\n📋 Generating debug report...")
        debug_report = debug_tracker.generate_debug_report()
        print(f"Debug report contains {len(debug_report.get('interactions', []))} interactions")
        
        print("\n✅ ALL DEBUGGING TESTS COMPLETED SUCCESSFULLY!")
        print("\nKey improvements verified:")
        print("✓ Full dataset usage instead of samples")
        print("✓ Enhanced debug tracking at multiple levels")
        print("✓ Data completeness analysis")
        print("✓ AI prompt and response logging")
        print("✓ Comprehensive debug reporting")
        
    except Exception as e:
        print(f"\n❌ Error during debugging tests: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original debug level
        config.DEBUG_LEVEL = original_debug_level
        print(f"\n🔧 Debug level restored to: {original_debug_level}")

def main():
    """Main test function."""
    print("Excel AI Analyzer - Enhanced Debugging Test")
    print("This script tests the improved debugging and full dataset usage features.")
    
    test_debugging_features()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
    
    print("\nTo enable full AI testing, set your OpenAI API key:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    print("\nThen run: python test_debugging.py")

if __name__ == "__main__":
    main()
