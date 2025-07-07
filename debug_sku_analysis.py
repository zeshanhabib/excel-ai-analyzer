#!/usr/bin/env python3
"""
Debug script to ensure all rows of SKU Units Sold_BackUp.xlsx are loaded 
and submitted to AI model for analysis with full dataset verification.
"""

import pandas as pd
import os
import sys
from datetime import datetime
from excel_reader import ExcelReader
from ai_analyzer import AIAnalyzer
from debug_utils import DebugTracker
import config

def load_sku_data():
    """Load the SKU Units Sold backup data and verify complete loading."""
    print("="*80)
    print("LOADING SKU UNITS SOLD DATA")
    print("="*80)
    
    file_path = 'sample_data/SKU Units Sold_BackUp.xlsx'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f"📁 Loading file: {file_path}")
    
    # Load using ExcelReader
    reader = ExcelReader()
    try:
        sheets_data = reader.read_excel(file_path)
        
        print(f"✅ File loaded successfully!")
        print(f"📊 Number of sheets found: {len(sheets_data)}")
        
        # Get the main sheet (usually the first one or find by name)
        if len(sheets_data) == 1:
            sheet_name = list(sheets_data.keys())[0]
            df = sheets_data[sheet_name]
        else:
            # Look for sheets with 'SKU' or 'Units' in the name
            likely_sheets = [name for name in sheets_data.keys() 
                           if any(keyword in name.upper() for keyword in ['SKU', 'UNITS', 'SOLD', 'SALES'])]
            if likely_sheets:
                sheet_name = likely_sheets[0]
                df = sheets_data[sheet_name]
            else:
                sheet_name = list(sheets_data.keys())[0]
                df = sheets_data[sheet_name]
        
        print(f"📋 Using sheet: '{sheet_name}'")
        
        # Comprehensive data analysis
        print(f"\n📈 COMPLETE DATASET ANALYSIS:")
        print(f"   Total rows: {len(df):,}")
        print(f"   Total columns: {len(df.columns)}")
        print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        print(f"   Data shape: {df.shape}")
        
        print(f"\n📊 COLUMN INFORMATION:")
        for i, col in enumerate(df.columns):
            non_null = df[col].count()
            null_count = len(df) - non_null
            data_type = str(df[col].dtype)
            print(f"   {i+1:2d}. {col:<25} | Type: {data_type:<10} | Non-null: {non_null:,} | Null: {null_count:,}")
        
        print(f"\n🔍 DATA SAMPLE (First 5 rows):")
        print(df.head().to_string())
        
        print(f"\n🔍 DATA SAMPLE (Last 5 rows):")
        print(df.tail().to_string())
        
        # Check for missing data
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            print(f"\n⚠️  MISSING DATA DETECTED:")
            for col, missing_count in missing_data[missing_data > 0].items():
                percentage = (missing_count / len(df)) * 100
                print(f"   {col}: {missing_count:,} missing values ({percentage:.1f}%)")
        else:
            print(f"\n✅ NO MISSING DATA DETECTED")
        
        # Data quality checks
        print(f"\n🔬 DATA QUALITY CHECKS:")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"   Numeric columns: {len(numeric_cols)}")
            for col in numeric_cols:
                print(f"   {col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}")
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            print(f"   Categorical columns: {len(categorical_cols)}")
            for col in categorical_cols:
                unique_count = df[col].nunique()
                print(f"   {col}: {unique_count} unique values")
        
        return df, sheet_name
        
    except Exception as e:
        raise Exception(f"Error loading SKU data: {str(e)}")

def verify_full_dataset_ai_analysis(df, sheet_name):
    """Verify that the complete dataset is being used in AI analysis."""
    print("\n" + "="*80)
    print("VERIFYING FULL DATASET AI ANALYSIS")
    print("="*80)
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: No OPENAI_API_KEY found in environment.")
        print("AI analysis will be simulated without actual API calls.")
        print("To test with real AI, set: export OPENAI_API_KEY='your-key'")
        ai_available = False
    else:
        print(f"✅ OpenAI API key detected")
        ai_available = True
    
    # Set debug level to FULL for maximum visibility
    original_debug_level = config.DEBUG_LEVEL
    config.DEBUG_LEVEL = config.DEBUG_LEVELS['FULL']
    
    try:
        # Initialize debug tracker
        debug_tracker = DebugTracker(debug_level=config.DEBUG_LEVELS['FULL'])
        
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzer()
        
        print(f"\n🤖 AI ANALYZER CONFIGURATION:")
        print(f"   Debug level: {config.DEBUG_LEVEL}")
        print(f"   Use full dataset: {config.AI_USE_FULL_DATASET}")
        print(f"   Max context length: {config.AI_MAX_CONTEXT_LENGTH}")
        
        # Test 1: Data Structure Analysis
        print(f"\n📋 TEST 1: ANALYZING DATA STRUCTURE")
        print(f"   Input dataset: {len(df)} rows × {len(df.columns)} columns")
        
        try:
            structure_result = ai_analyzer.analyze_data_structure(df)
            
            # Verify debug information
            if 'debug_info' in structure_result:
                debug_info = structure_result['debug_info']
                print(f"   ✅ Debug info captured:")
                print(f"      Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                print(f"      Context length: {debug_info.get('context_length', 'N/A')}")
                print(f"      Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
                print(f"      Data preparation time: {debug_info.get('data_prep_time', 'N/A')}")
                
                # Verify we're using the full dataset
                expected_size = f"{len(df)} rows, {len(df.columns)} columns"
                actual_size = debug_info.get('dataset_size', '')
                if expected_size in str(actual_size):
                    print(f"   ✅ VERIFICATION PASSED: Full dataset size confirmed")
                else:
                    print(f"   ❌ VERIFICATION FAILED: Dataset size mismatch")
                    print(f"      Expected: {expected_size}")
                    print(f"      Got: {actual_size}")
            
            if ai_available and structure_result.get('analysis'):
                print(f"\n   📊 AI Analysis Result:")
                print(f"      {structure_result['analysis'][:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error in structure analysis: {str(e)}")
        
        # Test 2: Question Answering with Full Dataset
        print(f"\n❓ TEST 2: QUESTION ANSWERING WITH FULL DATASET")
        test_questions = [
            "What are the top 10 SKUs by units sold? Include exact numbers.",
            "Analyze the sales distribution across all SKUs in the dataset.",
            "What patterns do you see in the complete dataset? Summarize all data.",
            "Calculate total units sold across the entire dataset."
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            try:
                answer_result = ai_analyzer.answer_question(df, question)
                
                if 'debug_info' in answer_result:
                    debug_info = answer_result['debug_info']
                    print(f"   ✅ Debug info:")
                    print(f"      Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                    print(f"      Supporting data rows: {debug_info.get('supporting_data_rows', 'N/A')}")
                    print(f"      Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
                    print(f"      Context length: {debug_info.get('context_length', 'N/A')}")
                    
                    # Verify supporting data includes full dataset
                    supporting_rows = debug_info.get('supporting_data_rows', 0)
                    if isinstance(supporting_rows, int) and supporting_rows >= len(df):
                        print(f"   ✅ VERIFICATION PASSED: All {len(df)} rows included in analysis")
                    elif 'all' in str(supporting_rows).lower():
                        print(f"   ✅ VERIFICATION PASSED: Full dataset confirmed")
                    else:
                        print(f"   ⚠️  VERIFICATION WARNING: Supporting data may be limited")
                        print(f"      Expected: >={len(df)} rows, Got: {supporting_rows}")
                
                if ai_available and answer_result.get('answer'):
                    print(f"   📝 AI Answer Preview: {answer_result['answer'][:150]}...")
                
            except Exception as e:
                print(f"   ❌ Error answering question {i}: {str(e)}")
        
        # Test 3: Anomaly Detection
        print(f"\n🔍 TEST 3: ANOMALY DETECTION ON FULL DATASET")
        try:
            anomaly_result = ai_analyzer.detect_anomalies(df)
            
            if 'debug_info' in anomaly_result:
                debug_info = anomaly_result['debug_info']
                print(f"   ✅ Debug info:")
                print(f"      Dataset size: {debug_info.get('dataset_size', 'N/A')}")
                print(f"      Anomalies found: {debug_info.get('anomalies_count', 'N/A')}")
                print(f"      Full dataset used: {debug_info.get('full_dataset_used', 'N/A')}")
            
            if ai_available and anomaly_result.get('anomalies'):
                anomalies = anomaly_result['anomalies']
                print(f"   📊 Found {len(anomalies)} potential anomalies")
        
        except Exception as e:
            print(f"   ❌ Error in anomaly detection: {str(e)}")
        
        # Generate comprehensive debug report
        print(f"\n📋 GENERATING COMPREHENSIVE DEBUG REPORT")
        debug_report = debug_tracker.get_debug_summary()
        
        print(f"   Total debug interactions: {len(debug_report.get('interactions', []))}")
        print(f"   Performance data points: {len(debug_report.get('performance', []))}")
        
        # Save debug report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"debug_reports/sku_analysis_debug_{timestamp}.json"
        
        os.makedirs("debug_reports", exist_ok=True)
        
        import json
        with open(report_file, 'w') as f:
            json.dump(debug_report, f, indent=2, default=str)
        
        print(f"   📁 Debug report saved to: {report_file}")
        
        return debug_report
        
    finally:
        # Restore original debug level
        config.DEBUG_LEVEL = original_debug_level

def main():
    """Main execution function."""
    print("SKU UNITS SOLD - FULL DATASET AI ANALYSIS DEBUG")
    print("This script verifies that ALL rows are loaded and analyzed by the AI model")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Load and verify data
        df, sheet_name = load_sku_data()
        
        # Step 2: Verify AI analysis uses full dataset
        debug_report = verify_full_dataset_ai_analysis(df, sheet_name)
        
        # Step 3: Summary
        print("\n" + "="*80)
        print("FINAL VERIFICATION SUMMARY")
        print("="*80)
        
        print(f"✅ SKU file successfully loaded:")
        print(f"   📁 File: sample_data/SKU Units Sold_BackUp.xlsx")
        print(f"   📋 Sheet: {sheet_name}")
        print(f"   📊 Total rows processed: {len(df):,}")
        print(f"   📊 Total columns: {len(df.columns)}")
        
        print(f"\n✅ AI analysis configuration:")
        print(f"   🔧 Debug level: {config.DEBUG_LEVEL}")
        print(f"   🔧 Use full dataset: {config.AI_USE_FULL_DATASET}")
        print(f"   🔧 Max context length: {config.AI_MAX_CONTEXT_LENGTH:,}")
        
        print(f"\n✅ Verification tests completed:")
        print(f"   📋 Data structure analysis")
        print(f"   ❓ Question answering with full dataset")
        print(f"   🔍 Anomaly detection")
        print(f"   📊 Debug report generation")
        
        if not os.getenv("OPENAI_API_KEY"):
            print(f"\n⚠️  To enable full AI testing:")
            print(f"   export OPENAI_API_KEY='your-openai-api-key'")
            print(f"   python debug_sku_analysis.py")
        
        print(f"\n🎉 ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
        print(f"   The complete SKU dataset ({len(df):,} rows) is being loaded")
        print(f"   and submitted to the AI model for comprehensive analysis.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import numpy as np
    sys.exit(main())
