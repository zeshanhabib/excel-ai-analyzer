import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import logging
import config
from debug_utils import DebugTracker, debug_performance, global_debug_tracker

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-powered data analysis using OpenAI GPT models with enhanced debugging."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", 
                 debug_tracker: Optional[DebugTracker] = None):
        """
        Initialize the AI Analyzer with enhanced debugging.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: OpenAI model to use
            debug_tracker: Custom debug tracker instance
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Initialize debug tracker
        self.debug_tracker = debug_tracker or global_debug_tracker
        
        self.debug_tracker.log_debug(f"Initializing AIAnalyzer", level=1, data={
            'api_key_exists': bool(self.api_key),
            'api_key_length': len(self.api_key) if self.api_key else 0,
            'model': self.model,
            'debug_level': self.debug_tracker.debug_level
        })
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.debug_tracker.log_debug("OpenAI client initialized successfully", level=1)
        except Exception as e:
            self.debug_tracker.log_debug(f"Error initializing OpenAI client: {e}", level=1)
            raise
    
    @debug_performance
    def analyze_data_structure(self, df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """
        Analyze the structure and content of a DataFrame using AI with full data context.
        
        Args:
            df: Pandas DataFrame to analyze
            context: Additional context about the data
            
        Returns:
            Dictionary with AI analysis results
        """
        self.debug_tracker.log_debug("Starting data structure analysis", level=1)
        
        # Track the input DataFrame
        df_tracking = self.debug_tracker.track_dataframe(df, "analyze_data_structure", "input")
        
        try:
            # Prepare comprehensive data summary for AI (NO TRUNCATION)
            data_summary = self._prepare_enhanced_data_summary(df)
            
            # Create enhanced prompt with full dataset context
            prompt = self._create_analysis_prompt(df, data_summary, context)
            
            self.debug_tracker.log_debug("Calling OpenAI for data structure analysis", level=2, data={
                'prompt_length': len(prompt),
                'model': self.model
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst expert. Analyze datasets and provide actionable insights based on the COMPLETE dataset provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # Increased for more detailed responses
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            # Track the AI interaction
            self.debug_tracker.track_ai_interaction(
                prompt, analysis, "analyze_data_structure", 
                self.model, response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            # Analyze data completeness
            completeness_analysis = self.debug_tracker.analyze_data_completeness(
                df, prompt, "analyze_data_structure"
            )
            
            # Create comprehensive debug info
            debug_info = self._create_comprehensive_debug_info(df, df_tracking, completeness_analysis, prompt)
            
            result = {
                "ai_analysis": analysis,
                "data_summary": data_summary,
                "completeness_metrics": completeness_analysis,
                "debug_info": debug_info,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            self.debug_tracker.log_debug("Data structure analysis completed", level=1)
            return result
            
        except Exception as e:
            self.debug_tracker.log_debug(f"Error in AI analysis: {str(e)}", level=1)
            logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "error": f"AI analysis failed: {str(e)}",
                "data_summary": self._prepare_enhanced_data_summary(df),
                "timestamp": pd.Timestamp.now().isoformat()
            }

    @debug_performance
    def answer_question(self, df: pd.DataFrame, question: str, context: str = "") -> Dict[str, Any]:
        """
        Answer a natural language question about the data using the COMPLETE dataset.
        
        Args:
            df: Pandas DataFrame
            question: Natural language question
            context: Additional context
            
        Returns:
            Dictionary with answer and supporting data
        """
        self.debug_tracker.log_debug(f"Starting question answering: '{question}'", level=1)
        
        # Track the input DataFrame
        df_tracking = self.debug_tracker.track_dataframe(df, "answer_question", "input")
        
        try:
            # Prepare COMPREHENSIVE data context (ensuring full dataset representation)
            data_info = self._prepare_enhanced_data_context(df)
            
            # Create enhanced prompt that ensures full dataset usage
            prompt = self._create_question_prompt(df, question, data_info, context)
            
            self.debug_tracker.log_debug("Making OpenAI API call for question answering", level=2, data={
                'question': question,
                'prompt_length': len(prompt),
                'model': self.model
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst. Answer questions about datasets using ALL available data. Provide comprehensive analysis based on the COMPLETE dataset context provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,  # Increased for more detailed responses
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Track the AI interaction
            self.debug_tracker.track_ai_interaction(
                prompt, answer, "answer_question", 
                self.model, response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            # Extract comprehensive supporting data
            supporting_data = self._extract_enhanced_supporting_data(df, question)
            
            # Analyze data completeness for this question
            completeness_analysis = self.debug_tracker.analyze_data_completeness(
                df, prompt, f"answer_question_{question[:50]}"
            )
            
            # Create comprehensive debug info
            debug_info = self._create_comprehensive_debug_info(df, df_tracking, completeness_analysis, prompt)
            
            result = {
                "question": question,
                "answer": answer,
                "supporting_data": supporting_data,
                "completeness_metrics": completeness_analysis,
                "debug_info": debug_info,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            self.debug_tracker.log_debug("Question answering completed successfully", level=1)
            return result
            
        except Exception as e:
            self.debug_tracker.log_debug(f"ERROR in answer_question: {str(e)}", level=1)
            import traceback
            self.debug_tracker.log_debug(f"Full traceback: {traceback.format_exc()}", level=2)
            logger.error(f"Error answering question: {str(e)}")
            return {
                "question": question,
                "error": f"Failed to answer question: {str(e)}",
                "timestamp": pd.Timestamp.now().isoformat()
            }
    
    def suggest_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggest appropriate visualizations for the dataset.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of visualization suggestions
        """
        try:
            data_info = self._prepare_data_context(df)
            
            prompt = f"""
            Suggest the best visualizations for this dataset:
            
            {data_info}
            
            For each suggestion, provide:
            1. Visualization type (bar chart, line chart, scatter plot, histogram, etc.)
            2. Which columns to use (x-axis, y-axis, color, etc.)
            3. Purpose of the visualization
            4. Key insights it would reveal
            
            Suggest 3-5 different visualizations that would be most valuable.
            Format as a JSON list with this structure:
            [
                {
                    "type": "chart_type",
                    "columns": {"x": "column_name", "y": "column_name", "color": "optional"},
                    "purpose": "description",
                    "insights": "what it reveals"
                }
            ]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Suggest the most effective charts for datasets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            # Try to parse JSON response, fallback to text if needed
            content = response.choices[0].message.content
            try:
                suggestions = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return a structured response
                suggestions = [{
                    "type": "multiple",
                    "description": content,
                    "purpose": "AI suggested visualizations",
                    "insights": "See full response for details"
                }]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting visualizations: {str(e)}")
            return [{
                "type": "error",
                "error": f"Failed to suggest visualizations: {str(e)}"
            }]
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect potential anomalies or outliers in the data.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            # Basic statistical anomaly detection
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            anomalies = {}
            
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    if len(outliers) > 0:
                        anomalies[col] = {
                            "count": len(outliers),
                            "percentage": (len(outliers) / len(df)) * 100,
                            "bounds": {"lower": lower_bound, "upper": upper_bound},
                            "outlier_values": outliers[col].tolist()[:10]  # Show first 10
                        }
            
            # Get AI interpretation
            if anomalies:
                anomaly_summary = {k: v['count'] for k, v in anomalies.items()}
                
                prompt = f"""
                Analyze these detected anomalies in the dataset:
                
                Anomaly Summary:
                {anomaly_summary}
                
                Dataset shape: {df.shape}
                Columns with anomalies: {list(anomalies.keys())}
                
                Please provide:
                1. Assessment of whether these anomalies are significant
                2. Possible explanations for the anomalies
                3. Recommendations for handling them
                4. Potential impact on analysis
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a data quality expert. Analyze anomalies and provide recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.3
                )
                
                ai_interpretation = response.choices[0].message.content
            else:
                ai_interpretation = "No significant anomalies detected using statistical methods."
            
            return {
                "anomalies": anomalies,
                "ai_interpretation": ai_interpretation,
                "total_anomalies": sum(v['count'] for v in anomalies.values()),
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return {
                "error": f"Anomaly detection failed: {str(e)}",
                "timestamp": pd.Timestamp.now().isoformat()
            }
    
    def _prepare_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare a concise data summary for AI analysis."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        summary = {
            "shape": df.shape,
            "columns": {
                "numeric": list(numeric_cols),
                "categorical": list(categorical_cols)
            },
            "missing_data": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum()
        }
        
        if len(numeric_cols) > 0:
            summary["numeric_stats"] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def _prepare_enhanced_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare a comprehensive data summary for AI analysis with NO DATA TRUNCATION."""
        self.debug_tracker.log_debug("Preparing enhanced data summary", level=2)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime']).columns
        
        # Comprehensive summary including ALL data characteristics
        summary = {
            "shape": df.shape,
            "total_cells": df.shape[0] * df.shape[1],
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
            "columns": {
                "numeric": list(numeric_cols),
                "categorical": list(categorical_cols),
                "datetime": list(datetime_cols),
                "total_count": len(df.columns)
            },
            "data_quality": {
                "missing_data": df.isnull().sum().to_dict(),
                "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
                "duplicates": df.duplicated().sum(),
                "duplicate_percentage": (df.duplicated().sum() / len(df) * 100)
            }
        }
        
        # Comprehensive numeric statistics (not just .describe())
        if len(numeric_cols) > 0:
            numeric_summary = {}
            for col in numeric_cols:
                if df[col].notna().sum() > 0:  # Only if column has data
                    numeric_summary[col] = {
                        "count": df[col].count(),
                        "mean": df[col].mean(),
                        "median": df[col].median(),
                        "std": df[col].std(),
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "quartiles": {
                            "q1": df[col].quantile(0.25),
                            "q3": df[col].quantile(0.75)
                        },
                        "percentiles": {
                            "p10": df[col].quantile(0.1),
                            "p90": df[col].quantile(0.9),
                            "p95": df[col].quantile(0.95),
                            "p99": df[col].quantile(0.99)
                        },
                        "unique_values": df[col].nunique(),
                        "zero_count": (df[col] == 0).sum(),
                        "negative_count": (df[col] < 0).sum(),
                        "positive_count": (df[col] > 0).sum()
                    }
            summary["numeric_analysis"] = numeric_summary
        
        # Comprehensive categorical analysis
        if len(categorical_cols) > 0:
            categorical_summary = {}
            for col in categorical_cols:
                if df[col].notna().sum() > 0:
                    value_counts = df[col].value_counts()
                    categorical_summary[col] = {
                        "unique_values": df[col].nunique(),
                        "most_frequent": df[col].mode().iloc[0] if not df[col].empty else None,
                        "most_frequent_count": value_counts.iloc[0] if len(value_counts) > 0 else 0,
                        "least_frequent": value_counts.index[-1] if len(value_counts) > 0 else None,
                        "least_frequent_count": value_counts.iloc[-1] if len(value_counts) > 0 else 0,
                        "value_distribution": value_counts.to_dict(),  # ALL values, not just top 5
                        "text_length_stats": {
                            "min_length": df[col].astype(str).str.len().min(),
                            "max_length": df[col].astype(str).str.len().max(),
                            "avg_length": df[col].astype(str).str.len().mean()
                        } if df[col].dtype == 'object' else None
                    }
            summary["categorical_analysis"] = categorical_summary
        
        # Data patterns and relationships
        summary["data_patterns"] = {
            "correlation_pairs": [],
            "potential_keys": [],
            "data_ranges": {}
        }
        
        # Find potential primary keys
        for col in df.columns:
            if df[col].nunique() == len(df) and df[col].notna().all():
                summary["data_patterns"]["potential_keys"].append(col)
        
        # High correlation pairs for numeric data
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation
                        high_corr_pairs.append({
                            "col1": corr_matrix.columns[i],
                            "col2": corr_matrix.columns[j],
                            "correlation": corr_val
                        })
            summary["data_patterns"]["correlation_pairs"] = high_corr_pairs
        
        self.debug_tracker.log_debug("Enhanced data summary prepared", level=2, data={
            "summary_components": list(summary.keys()),
            "numeric_cols_analyzed": len(numeric_cols),
            "categorical_cols_analyzed": len(categorical_cols)
        })
        
        return summary

    def _prepare_enhanced_data_context(self, df: pd.DataFrame) -> str:
        """Prepare comprehensive data context string ensuring FULL dataset representation."""
        self.debug_tracker.log_debug("Preparing enhanced data context", level=2)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Start with comprehensive overview
        context_parts = [
            f"=== COMPLETE DATASET ANALYSIS ===",
            f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns",
            f"Total Data Points: {df.shape[0] * df.shape[1]:,}",
            f"Memory Usage: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB",
            f"",
            f"=== COLUMN INFORMATION ===",
            f"Numeric Columns ({len(numeric_cols)}): {list(numeric_cols)}",
            f"Categorical Columns ({len(categorical_cols)}): {list(categorical_cols)}",
            f"Data Types: {df.dtypes.to_dict()}",
            f""
        ]
        
        # Add missing data analysis
        missing_info = df.isnull().sum()
        if missing_info.sum() > 0:
            context_parts.extend([
                f"=== MISSING DATA ANALYSIS ===",
                f"Total Missing Values: {missing_info.sum():,}",
                f"Missing by Column: {missing_info[missing_info > 0].to_dict()}",
                f"Missing Percentages: {(missing_info[missing_info > 0] / len(df) * 100).round(2).to_dict()}",
                f""
            ])
        
        # Add comprehensive sample data (more than just 3 rows)
        sample_size = min(10, len(df))  # Show up to 10 rows instead of 3
        if config.AI_USE_FULL_DATASET and sample_size > 0:
            context_parts.extend([
                f"=== COMPREHENSIVE DATA SAMPLE ({sample_size} rows) ===",
                df.head(sample_size).to_string(max_cols=None),
                f""
            ])
            
            # Add tail sample for better representation
            if len(df) > sample_size:
                context_parts.extend([
                    f"=== DATA SAMPLE FROM END ({min(5, len(df) - sample_size)} rows) ===",
                    df.tail(min(5, len(df) - sample_size)).to_string(max_cols=None),
                    f""
                ])
        
        # Add CRITICAL TOP VALUES section for accuracy in top/highest queries
        if len(numeric_cols) > 0:
            context_parts.extend([
                f"=== CRITICAL TOP VALUES (USE FOR TOP/HIGHEST QUESTIONS) ===",
                f"IMPORTANT: When asked about 'top', 'highest', 'most', 'maximum' values,"
            ])
            
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    # Get top 10 values with their indices
                    top_values = df.nlargest(10, col)
                    context_parts.append(f"TOP 10 {col}:")
                    for i, (idx, row) in enumerate(top_values.iterrows(), 1):
                        # Include key columns for context
                        row_info = f"  #{i}: {row[col]}"
                        # Add other meaningful columns for context
                        other_cols = [c for c in df.columns if c != col and not df[c].isna().all()][:3]
                        if other_cols:
                            other_values = [f"{c}={row[c]}" for c in other_cols if pd.notna(row[c])]
                            if other_values:
                                row_info += f" ({', '.join(other_values)})"
                        context_parts.append(row_info)
                    context_parts.append("")
            
            context_parts.append("*** ALWAYS use the above TOP VALUES when answering questions about highest/most/top values ***")
            context_parts.append("")
        
        # Add comprehensive numeric statistics
        if len(numeric_cols) > 0:
            context_parts.extend([
                f"=== COMPLETE NUMERIC ANALYSIS ===",
                df[numeric_cols].describe(percentiles=[.1, .25, .5, .75, .9, .95, .99]).to_string(),
                f""
            ])
            
            # Add distribution information
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    context_parts.append(f"{col} Distribution: Min={df[col].min()}, Max={df[col].max()}, "
                                       f"Unique Values={df[col].nunique()}, "
                                       f"Zeros={sum(df[col] == 0)}, "
                                       f"Negatives={sum(df[col] < 0)}")
            context_parts.append("")
        
        # Add comprehensive categorical analysis
        if len(categorical_cols) > 0:
            context_parts.append("=== COMPLETE CATEGORICAL ANALYSIS ===")
            for col in categorical_cols:
                if df[col].notna().sum() > 0:
                    value_counts = df[col].value_counts()
                    context_parts.extend([
                        f"{col} ({df[col].nunique()} unique values):",
                        f"  Most frequent: {value_counts.index[0]} ({value_counts.iloc[0]} times)",
                        f"  All values: {value_counts.to_dict()}",
                        f""
                    ])
        
        # Add data quality summary
        context_parts.extend([
            f"=== DATA QUALITY SUMMARY ===",
            f"Duplicate Rows: {df.duplicated().sum()} ({df.duplicated().sum()/len(df)*100:.2f}%)",
            f"Complete Rows: {len(df) - df.isnull().any(axis=1).sum()} ({(len(df) - df.isnull().any(axis=1).sum())/len(df)*100:.2f}%)",
            f"Data Completeness: {((df.size - df.isnull().sum().sum()) / df.size * 100):.2f}%"
        ])
        
        full_context = "\n".join(context_parts)
        
        # Check if context is within reasonable limits
        if len(full_context) > config.AI_MAX_CONTEXT_LENGTH:
            self.debug_tracker.log_debug(
                f"Context length ({len(full_context)}) exceeds limit ({config.AI_MAX_CONTEXT_LENGTH}), truncating intelligently",
                level=1
            )
            # Intelligent truncation - keep essential parts
            essential_parts = context_parts[:10] + context_parts[-5:]  # Keep overview and summary
            full_context = "\n".join(essential_parts)
        
        self.debug_tracker.log_debug("Enhanced data context prepared", level=2, data={
            "context_length": len(full_context),
            "sample_rows_included": sample_size,
            "components_included": len(context_parts)
        })
        
        return full_context

    def _create_analysis_prompt(self, df: pd.DataFrame, data_summary: Dict, context: str) -> str:
        """Create comprehensive analysis prompt ensuring full dataset consideration."""
        data_context = self._prepare_enhanced_data_context(df)
        
        prompt = f"""
        You are analyzing a COMPLETE dataset. Use ALL the information provided below to give comprehensive insights.
        
        IMPORTANT: Base your analysis on the ENTIRE dataset context provided, not just samples.
        
        {data_context}
        
        Additional Context: {context}
        
        Please provide a comprehensive analysis covering:
        
        1. **Data Quality Assessment** (based on ALL {df.shape[0]} rows):
           - Overall data completeness and reliability
           - Data integrity issues across the entire dataset
           - Recommendations for data cleaning
        
        2. **Complete Statistical Analysis**:
           - Key patterns observed across all data points
           - Distribution characteristics for all numeric columns
           - Frequency analysis for all categorical variables
        
        3. **Business Insights** (derived from the full dataset):
           - Key trends and patterns in the complete data
           - Outliers and anomalies that stand out
           - Actionable recommendations based on comprehensive analysis
        
        4. **Data Relationships**:
           - Correlations and dependencies identified
           - Cross-column patterns and relationships
        
        5. **Further Analysis Recommendations**:
           - Specific analyses that would benefit from this complete dataset
           - Visualization suggestions that would reveal insights
        
        Remember: You have access to the COMPLETE dataset information. Use all of it for your analysis.
        """
        
        return prompt

    def _create_question_prompt(self, df: pd.DataFrame, question: str, data_info: str, context: str) -> str:
        """Create question-answering prompt ensuring full dataset usage."""
        
        # Detect if this is a top/highest question for special handling
        question_lower = question.lower()
        is_top_question = any(word in question_lower for word in ["top", "highest", "most", "maximum", "largest", "best"])
        
        base_prompt = f"""
        Answer this question about the COMPLETE dataset: "{question}"
        
        You have access to the FULL dataset with {df.shape[0]} rows and {df.shape[1]} columns.
        Use ALL available information to provide the most accurate and comprehensive answer.
        
        COMPLETE DATASET INFORMATION:
        {data_info}
        
        Additional Context: {context}
        """
        
        if is_top_question:
            base_prompt += f"""
        
        *** CRITICAL INSTRUCTION FOR TOP/HIGHEST QUESTIONS ***
        This question asks about TOP/HIGHEST values. You MUST use the "CRITICAL TOP VALUES" section 
        from the dataset information above. Do NOT use the sample data rows - use the pre-calculated 
        TOP 10 values which represent the actual highest values in the complete dataset.
        
        SPECIFICALLY:
        - Look for the "=== CRITICAL TOP VALUES ===" section
        - Use those exact rankings and values
        - These are the definitive top values from all {df.shape[0]} rows
        - Sample data rows may not contain the highest values
        """
        
        base_prompt += f"""
        
        Instructions for answering:
        1. Base your answer on the ENTIRE dataset (all {df.shape[0]} rows)
        2. Use specific numbers and statistics from the complete data
        3. If calculations are needed, consider all relevant data points
        4. Provide supporting evidence from the full dataset
        5. If trends or patterns are mentioned, ensure they represent the complete data
        
        Please provide:
        1. **Direct Answer**: Clear response to the question using complete dataset
        2. **Supporting Evidence**: Specific data points and statistics from all {df.shape[0]} rows
        3. **Methodology**: How you derived the answer from the complete dataset
        4. **Confidence Level**: How confident you are in the answer given the complete data available
        5. **Additional Insights**: Related findings from the full dataset that might be relevant
        
        If the question cannot be fully answered with the complete dataset provided, explain exactly what additional data would be needed.
        """
        
        return base_prompt

    def _extract_enhanced_supporting_data(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Extract comprehensive supporting data based on the question using FULL dataset."""
        self.debug_tracker.log_debug("Extracting enhanced supporting data", level=2)
        
        question_lower = question.lower()
        supporting_data = {
            "dataset_size": {"rows": len(df), "columns": len(df.columns)},
            "data_coverage": "complete_dataset"
        }
        
        # Comprehensive data extraction based on question keywords
        if any(word in question_lower for word in ["top", "highest", "maximum", "largest", "best"]):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    top_10 = df.nlargest(10, col)[[col]].to_dict()[col]
                    supporting_data[f"top_10_{col}"] = list(top_10.values())
                    supporting_data[f"top_10_{col}_indices"] = list(top_10.keys())
        
        if any(word in question_lower for word in ["bottom", "lowest", "minimum", "smallest", "worst"]):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    bottom_10 = df.nsmallest(10, col)[[col]].to_dict()[col]
                    supporting_data[f"bottom_10_{col}"] = list(bottom_10.values())
                    supporting_data[f"bottom_10_{col}_indices"] = list(bottom_10.keys())
        
        if any(word in question_lower for word in ["average", "mean", "typical"]):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                supporting_data["complete_averages"] = df[numeric_cols].mean().to_dict()
                supporting_data["complete_medians"] = df[numeric_cols].median().to_dict()
        
        if any(word in question_lower for word in ["count", "total", "number", "how many"]):
            supporting_data["total_rows"] = len(df)
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df[col].notna().sum() > 0:
                    complete_counts = df[col].value_counts().to_dict()
                    supporting_data[f"complete_{col}_counts"] = complete_counts
        
        if any(word in question_lower for word in ["distribution", "spread", "range", "variance"]):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].notna().sum() > 0:
                    supporting_data[f"{col}_distribution"] = {
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "range": df[col].max() - df[col].min(),
                        "std": df[col].std(),
                        "variance": df[col].var(),
                        "percentiles": {
                            "p25": df[col].quantile(0.25),
                            "p50": df[col].quantile(0.50),
                            "p75": df[col].quantile(0.75),
                            "p90": df[col].quantile(0.90),
                            "p95": df[col].quantile(0.95)
                        }
                    }
        
        if any(word in question_lower for word in ["correlation", "relationship", "related"]):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                supporting_data["correlation_matrix"] = corr_matrix.to_dict()
        
        # Add summary statistics for all columns mentioned in question
        for col in df.columns:
            if col.lower() in question_lower:
                if col in df.select_dtypes(include=[np.number]).columns:
                    supporting_data[f"{col}_complete_stats"] = {
                        "count": df[col].count(),
                        "mean": df[col].mean(),
                        "median": df[col].median(),
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "unique_values": df[col].nunique()
                    }
                else:
                    supporting_data[f"{col}_complete_stats"] = {
                        "count": df[col].count(),
                        "unique_values": df[col].nunique(),
                        "value_counts": df[col].value_counts().to_dict()
                    }
        
        self.debug_tracker.log_debug("Enhanced supporting data extracted", level=2, data={
            "supporting_data_keys": list(supporting_data.keys()),
            "data_points_included": len(supporting_data)
        })
        
        return supporting_data

    def _create_comprehensive_debug_info(self, df: pd.DataFrame, df_tracking: Dict, 
                                       completeness_analysis: Dict, prompt: str) -> Dict[str, Any]:
        """Create comprehensive debug information for analysis results."""
        return {
            'dataset_size': f"{df.shape[0]} rows, {df.shape[1]} columns",
            'dataset_rows': df.shape[0],
            'dataset_cols': df.shape[1],
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'context_length': len(prompt),
            'full_dataset_used': config.AI_USE_FULL_DATASET,
            'data_prep_time': df_tracking.get('processing_time', 'N/A'),
            'column_coverage': completeness_analysis.get('column_coverage', 1.0),
            'sample_coverage': completeness_analysis.get('sample_coverage', 1.0),
            'original_rows': completeness_analysis.get('original_rows', df.shape[0]),
            'processed_rows': completeness_analysis.get('processed_rows', df.shape[0]),
            'data_truncated': completeness_analysis.get('sample_coverage', 1.0) < 0.95,
            'truncation_reason': completeness_analysis.get('truncation_reason', None),
            'supporting_data_rows': completeness_analysis.get('processed_rows', df.shape[0]),
            'data_quality_score': self._calculate_data_quality_score(df),
            'debug_level': self.debug_tracker.debug_level
        }
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate a data quality score (0-1) based on completeness and consistency."""
        # Calculate missing data percentage
        missing_percentage = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
        
        # Calculate duplicate percentage
        duplicate_percentage = df.duplicated().sum() / df.shape[0]
        
        # Simple quality score (can be enhanced)
        quality_score = 1.0 - (missing_percentage * 0.5) - (duplicate_percentage * 0.3)
        return max(0.0, min(1.0, quality_score))

    # ...existing code for other methods...
