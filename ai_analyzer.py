import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-powered data analysis using OpenAI GPT models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the AI Analyzer.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        print(f"DEBUG: API key exists: {bool(self.api_key)}")
        print(f"DEBUG: API key length: {len(self.api_key) if self.api_key else 0}")
        print(f"DEBUG: Model: {self.model}")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            print("DEBUG: OpenAI client initialized successfully")
        except Exception as e:
            print(f"DEBUG: Error initializing OpenAI client: {e}")
            raise
        
    def analyze_data_structure(self, df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """
        Analyze the structure and content of a DataFrame using AI.
        
        Args:
            df: Pandas DataFrame to analyze
            context: Additional context about the data
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            # Prepare data summary for AI
            data_summary = self._prepare_data_summary(df)
            
            prompt = f"""
            Analyze this dataset and provide insights:
            
            Data Summary:
            - Shape: {df.shape}
            - Columns: {list(df.columns)}
            - Data types: {df.dtypes.to_dict()}
            - Sample data (first 3 rows):
            {df.head(3).to_string()}
            
            {context}
            
            Please provide:
            1. Data quality assessment
            2. Key patterns or trends you notice
            3. Potential data issues or anomalies
            4. Suggestions for further analysis
            5. Business insights (if applicable)
            
            Format your response as structured text with clear sections.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst expert. Analyze datasets and provide actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "ai_analysis": analysis,
                "data_summary": data_summary,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "error": f"AI analysis failed: {str(e)}",
                "data_summary": self._prepare_data_summary(df),
                "timestamp": pd.Timestamp.now().isoformat()
            }
    
    def answer_question(self, df: pd.DataFrame, question: str, context: str = "") -> Dict[str, Any]:
        """
        Answer a natural language question about the data.
        
        Args:
            df: Pandas DataFrame
            question: Natural language question
            context: Additional context
            
        Returns:
            Dictionary with answer and supporting data
        """
        print(f"DEBUG: answer_question called with question: '{question}'")
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        
        try:
            print("DEBUG: Starting to prepare data context...")
            # Prepare data for AI context
            data_info = self._prepare_data_context(df)
            print(f"DEBUG: Data context prepared, length: {len(data_info)} characters")
            
            prompt = f"""
            Answer this question about the dataset: "{question}"
            
            Dataset Information:
            {data_info}
            
            Context: {context}
            
            Please provide:
            1. A direct answer to the question
            2. Supporting data/statistics
            3. Any relevant insights
            4. If you need to perform calculations, describe the method
            
            If the question cannot be answered with the available data, explain what additional data would be needed.
            """
            
            print(f"DEBUG: Prompt prepared, length: {len(prompt)} characters")
            print("DEBUG: Making OpenAI API call...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst. Answer questions about datasets clearly and provide supporting evidence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            print("DEBUG: OpenAI API call successful!")
            answer = response.choices[0].message.content
            print(f"DEBUG: Answer received, length: {len(answer)} characters")
            
            # Try to extract specific data based on the question
            print("DEBUG: Extracting supporting data...")
            supporting_data = self._extract_supporting_data(df, question)
            print(f"DEBUG: Supporting data extracted: {supporting_data}")
            
            result = {
                "question": question,
                "answer": answer,
                "supporting_data": supporting_data,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            print("DEBUG: answer_question completed successfully!")
            return result
            
        except Exception as e:
            print(f"DEBUG: ERROR in answer_question: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
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
    
    def _prepare_data_context(self, df: pd.DataFrame) -> str:
        """Prepare data context string for AI prompts."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        context = f"""
        Dataset Overview:
        - Shape: {df.shape[0]} rows, {df.shape[1]} columns
        - Numeric columns: {list(numeric_cols)}
        - Categorical columns: {list(categorical_cols)}
        - Missing values: {df.isnull().sum().sum()} total
        
        Sample Data (first 3 rows):
        {df.head(3).to_string()}
        """
        
        if len(numeric_cols) > 0:
            context += f"\n\nNumeric Summary:\n{df[numeric_cols].describe().to_string()}"
        
        return context
    
    def _extract_supporting_data(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Extract relevant data based on the question."""
        question_lower = question.lower()
        supporting_data = {}
        
        # Simple keyword-based data extraction
        if "top" in question_lower or "highest" in question_lower:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols:
                    top_values = df.nlargest(5, col)[col].tolist()
                    supporting_data[f"top_5_{col}"] = top_values
        
        if "average" in question_lower or "mean" in question_lower:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                supporting_data["averages"] = df[numeric_cols].mean().to_dict()
        
        if "count" in question_lower or "total" in question_lower:
            supporting_data["row_count"] = len(df)
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                supporting_data[f"{col}_counts"] = df[col].value_counts().head().to_dict()
        
        return supporting_data
