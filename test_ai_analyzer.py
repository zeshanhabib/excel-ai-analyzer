#!/usr/bin/env python3
"""
Test script to debug the AI analyzer functionality
"""

import sys
import os
import pandas as pd
from ai_analyzer import AIAnalyzer

def test_ai_analyzer():
    print("🔍 Testing AI Analyzer...")
    
    # Load the inventory data
    try:
        df = pd.read_excel('sample_data/inventory_data.xlsx')
        print(f"✅ Loaded inventory data: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"📊 First few rows:")
        print(df.head().to_string())
        
        # Initialize AI analyzer
        analyzer = AIAnalyzer()
        
        # Test analysis
        prompt = "Analyze this inventory data and provide insights about stock levels, reorder needs, and trends."
        result = analyzer.answer_question(df, prompt)
        
        print(f"\n🤖 AI Analysis Result:")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success!")
            print(f"Question: {result.get('question', 'N/A')}")
            print(f"Answer: {result.get('answer', 'N/A')}")
            print(f"Supporting Data: {result.get('supporting_data', {})}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_analyzer()
