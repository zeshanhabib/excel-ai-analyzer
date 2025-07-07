"""
Enhanced debugging utilities for Excel AI Analyzer.
Provides comprehensive debugging and data tracking capabilities.
"""

import os
import json
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from functools import wraps
import config

# Setup debug logger
debug_logger = logging.getLogger('debug')
debug_logger.setLevel(logging.DEBUG)

# Create debug log handler if debug saving is enabled
if config.DEBUG_SAVE_DEBUG_LOGS:
    debug_handler = logging.FileHandler(config.DEBUG_LOG_FILE)
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    debug_handler.setFormatter(debug_formatter)
    debug_logger.addHandler(debug_handler)

class DebugTracker:
    """Enhanced debugging and data tracking for AI analysis."""
    
    def __init__(self, debug_level: Optional[int] = None):
        """Initialize debug tracker with specified level."""
        self.debug_level = debug_level or config.DEBUG_LEVEL
        self.session_data = {}
        self.performance_metrics = {}
        self.data_flow_log = []
        self.ai_interaction_log = []
        
    def log_debug(self, message: str, level: int = 1, data: Optional[Dict] = None):
        """Log debug message with appropriate level filtering."""
        if self.debug_level >= level:
            timestamp = datetime.now().isoformat()
            debug_entry = {
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'data': data or {}
            }
            
            # Console output
            print(f"[DEBUG L{level}] {message}")
            if data and self.debug_level >= config.DEBUG_LEVELS['DETAILED']:
                print(f"  Data: {json.dumps(data, default=str, indent=2)}")
            
            # File logging
            if config.DEBUG_SAVE_DEBUG_LOGS:
                debug_logger.debug(f"L{level}: {message} | Data: {data}")
            
            self.data_flow_log.append(debug_entry)
    
    def track_dataframe(self, df: pd.DataFrame, context: str, stage: str = "processing") -> Dict[str, Any]:
        """Track DataFrame properties and content for debugging."""
        tracking_info = {
            'context': context,
            'stage': stage,
            'timestamp': datetime.now().isoformat(),
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'null_counts': df.isnull().sum().to_dict(),
            'total_nulls': df.isnull().sum().sum(),
            'duplicate_count': df.duplicated().sum()
        }
        
        # Add sample data if debug level is high enough
        if self.debug_level >= config.DEBUG_LEVELS['DETAILED']:
            tracking_info['sample_head'] = df.head(3).to_dict()
            tracking_info['sample_tail'] = df.tail(3).to_dict()
        
        # Add comprehensive statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            tracking_info['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Add categorical summaries
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols:
                cat_summary[col] = {
                    'unique_count': df[col].nunique(),
                    'top_values': df[col].value_counts().head(5).to_dict()
                }
            tracking_info['categorical_summary'] = cat_summary
        
        self.log_debug(
            f"DataFrame tracking - {context} at {stage}",
            level=1,
            data={
                'shape': tracking_info['shape'],
                'memory_mb': round(tracking_info['memory_usage_mb'], 2),
                'null_percentage': round((tracking_info['total_nulls'] / (df.shape[0] * df.shape[1])) * 100, 2)
            }
        )
        
        # Store for session analysis
        session_key = f"{context}_{stage}"
        self.session_data[session_key] = tracking_info
        
        return tracking_info
    
    def track_ai_interaction(self, prompt: str, response: str, context: str, 
                           model: str, tokens_used: Optional[int] = None) -> Dict[str, Any]:
        """Track AI interactions for debugging."""
        interaction_info = {
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'prompt_length': len(prompt),
            'response_length': len(response),
            'tokens_used': tokens_used,
            'prompt_preview': prompt[:500] + "..." if len(prompt) > 500 else prompt,
            'response_preview': response[:500] + "..." if len(response) > 500 else response
        }
        
        # Store full prompt and response if debug level is maximum
        if self.debug_level >= config.DEBUG_LEVELS['FULL']:
            interaction_info['full_prompt'] = prompt
            interaction_info['full_response'] = response
        
        self.log_debug(
            f"AI Interaction - {context}",
            level=2,
            data={
                'model': model,
                'prompt_length': interaction_info['prompt_length'],
                'response_length': interaction_info['response_length'],
                'tokens_used': tokens_used
            }
        )
        
        self.ai_interaction_log.append(interaction_info)
        return interaction_info
    
    def analyze_data_completeness(self, original_df: pd.DataFrame, 
                                processed_data: str, context: str) -> Dict[str, Any]:
        """Analyze if processed data maintains completeness for AI analysis."""
        analysis = {
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'original_rows': len(original_df),
            'original_cols': len(original_df.columns),
            'processed_data_length': len(processed_data),
            'data_reduction_ratio': len(processed_data) / (original_df.shape[0] * original_df.shape[1])
        }
        
        # Check if key information is preserved
        analysis['columns_mentioned'] = sum(1 for col in original_df.columns 
                                          if col.lower() in processed_data.lower())
        analysis['column_coverage'] = analysis['columns_mentioned'] / len(original_df.columns)
        
        # Estimate data sample coverage
        sample_rows_found = processed_data.count('\n') - processed_data.count('Sample Data')
        analysis['estimated_sample_rows'] = max(0, sample_rows_found)
        analysis['sample_coverage'] = min(1.0, analysis['estimated_sample_rows'] / len(original_df))
        
        self.log_debug(
            f"Data completeness analysis - {context}",
            level=2,
            data={
                'column_coverage': round(analysis['column_coverage'] * 100, 2),
                'sample_coverage': round(analysis['sample_coverage'] * 100, 2),
                'data_length': analysis['processed_data_length']
            }
        )
        
        # Flag potential data loss
        if analysis['column_coverage'] < 0.8:
            self.log_debug(
                f"WARNING: Low column coverage in {context} - only {analysis['column_coverage']:.2%} columns mentioned",
                level=1
            )
        
        if analysis['sample_coverage'] < 0.1:
            self.log_debug(
                f"WARNING: Low sample coverage in {context} - only {analysis['sample_coverage']:.2%} of data sampled",
                level=1
            )
        
        return analysis
    
    def get_debug_summary(self) -> Dict[str, Any]:
        """Get comprehensive debug summary for the session."""
        return {
            'debug_level': self.debug_level,
            'session_start': min([entry['timestamp'] for entry in self.data_flow_log]) if self.data_flow_log else None,
            'total_debug_entries': len(self.data_flow_log),
            'ai_interactions': len(self.ai_interaction_log),
            'tracked_datasets': list(self.session_data.keys()),
            'performance_metrics': self.performance_metrics,
            'data_flow_summary': self.data_flow_log,
            'ai_interaction_summary': self.ai_interaction_log
        }
    
    def generate_debug_report(self) -> Dict[str, Any]:
        """Generate comprehensive debug report (alias for get_debug_summary)."""
        return self.get_debug_summary()
    
    def export_debug_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive debug report to file."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use debug_reports directory if it exists, otherwise current directory
            reports_dir = "debug_reports" if os.path.exists("debug_reports") else "."
            filepath = os.path.join(reports_dir, f"debug_report_{timestamp}.json")
        
        debug_summary = self.get_debug_summary()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(debug_summary, f, indent=2, default=str)
            
            self.log_debug(f"Debug report exported to {filepath}", level=1)
            return filepath
        except Exception as e:
            self.log_debug(f"Failed to export debug report: {str(e)}", level=1)
            return None

def debug_performance(func):
    """Decorator to track function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Try to get debug tracker from args/kwargs or create temporary one
        debug_tracker = None
        for arg in args:
            if isinstance(arg, DebugTracker):
                debug_tracker = arg
                break
        
        if not debug_tracker:
            debug_tracker = DebugTracker()
        
        execution_time = end_time - start_time
        debug_tracker.performance_metrics[func.__name__] = {
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        debug_tracker.log_debug(
            f"Performance: {func.__name__} executed in {execution_time:.3f}s",
            level=2
        )
        
        return result
    return wrapper

# Global debug tracker instance
global_debug_tracker = DebugTracker()
