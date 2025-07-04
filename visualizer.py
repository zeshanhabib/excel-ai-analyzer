import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DataVisualizer:
    """Create interactive visualizations for Excel data analysis."""
    
    def __init__(self):
        # Set default styling
        self.color_palette = px.colors.qualitative.Set3
        self.theme = "plotly_white"
        
    def create_overview_dashboard(self, df: pd.DataFrame, title: str = "Data Overview") -> go.Figure:
        """
        Create an overview dashboard with multiple subplots.
        
        Args:
            df: Pandas DataFrame
            title: Dashboard title
            
        Returns:
            Plotly figure with multiple subplots
        """
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            # Create subplots
            rows = 2
            cols = 2
            subplot_titles = ["Data Types Distribution", "Missing Values", "Numeric Distributions", "Categorical Distributions"]
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=subplot_titles,
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "histogram"}, {"type": "bar"}]]
            )
            
            # 1. Data types distribution (pie chart)
            type_counts = {"Numeric": len(numeric_cols), "Categorical": len(categorical_cols)}
            fig.add_trace(
                go.Pie(labels=list(type_counts.keys()), values=list(type_counts.values()),
                       name="Data Types"),
                row=1, col=1
            )
            
            # 2. Missing values (bar chart)
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0].head(10)  # Top 10 columns with missing data
            if len(missing_data) > 0:
                fig.add_trace(
                    go.Bar(x=missing_data.index, y=missing_data.values,
                           name="Missing Values"),
                    row=1, col=2
                )
            
            # 3. Numeric distributions (histogram for first numeric column)
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                fig.add_trace(
                    go.Histogram(x=df[col], name=f"{col} Distribution"),
                    row=2, col=1
                )
            
            # 4. Categorical distributions (bar chart for first categorical column)
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                value_counts = df[col].value_counts().head(10)
                fig.add_trace(
                    go.Bar(x=value_counts.index, y=value_counts.values,
                           name=f"{col} Counts"),
                    row=2, col=2
                )
            
            fig.update_layout(
                title_text=title,
                height=800,
                showlegend=False,
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating overview dashboard: {str(e)}")
            # Return empty figure on error
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def create_correlation_matrix(self, df: pd.DataFrame) -> go.Figure:
        """
        Create an interactive correlation heatmap.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Plotly heatmap figure
        """
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return go.Figure().add_annotation(
                    text="No numeric columns found for correlation analysis",
                    x=0.5, y=0.5
                )
            
            correlation_matrix = numeric_df.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Correlation Matrix",
                template=self.theme,
                width=600,
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating correlation matrix: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def create_distribution_plots(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> List[go.Figure]:
        """
        Create distribution plots for numeric columns.
        
        Args:
            df: Pandas DataFrame
            columns: Specific columns to plot (if None, plots all numeric columns)
            
        Returns:
            List of Plotly figures
        """
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if columns:
                numeric_cols = [col for col in columns if col in numeric_cols]
            
            figures = []
            
            for col in numeric_cols[:6]:  # Limit to first 6 columns
                fig = go.Figure()
                
                # Histogram
                fig.add_trace(go.Histogram(
                    x=df[col],
                    name="Distribution",
                    opacity=0.7,
                    nbinsx=30
                ))
                
                # Add mean line
                mean_val = df[col].mean()
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                             annotation_text=f"Mean: {mean_val:.2f}")
                
                fig.update_layout(
                    title=f"Distribution of {col}",
                    xaxis_title=col,
                    yaxis_title="Frequency",
                    template=self.theme
                )
                
                figures.append(fig)
            
            return figures
            
        except Exception as e:
            logger.error(f"Error creating distribution plots: {str(e)}")
            return [go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)]
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str,
                           color_col: Optional[str] = None, size_col: Optional[str] = None) -> go.Figure:
        """
        Create an interactive scatter plot.
        
        Args:
            df: Pandas DataFrame
            x_col: Column for x-axis
            y_col: Column for y-axis
            color_col: Column for color coding (optional)
            size_col: Column for size coding (optional)
            
        Returns:
            Plotly scatter plot figure
        """
        try:
            fig = px.scatter(
                df, x=x_col, y=y_col,
                color=color_col,
                size=size_col,
                hover_data=df.columns.tolist(),
                template=self.theme
            )
            
            fig.update_layout(
                title=f"{y_col} vs {x_col}",
                xaxis_title=x_col,
                yaxis_title=y_col
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def create_time_series_plot(self, df: pd.DataFrame, date_col: str, value_cols: List[str]) -> go.Figure:
        """
        Create a time series plot.
        
        Args:
            df: Pandas DataFrame
            date_col: Column containing dates
            value_cols: Columns to plot over time
            
        Returns:
            Plotly line plot figure
        """
        try:
            fig = go.Figure()
            
            # Convert date column to datetime if needed
            if df[date_col].dtype == 'object':
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            for i, col in enumerate(value_cols):
                fig.add_trace(go.Scatter(
                    x=df[date_col],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=self.color_palette[i % len(self.color_palette)])
                ))
            
            fig.update_layout(
                title="Time Series Analysis",
                xaxis_title=date_col,
                yaxis_title="Values",
                template=self.theme,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating time series plot: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def create_box_plot(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> go.Figure:
        """
        Create box plots for numeric columns to show distributions and outliers.
        
        Args:
            df: Pandas DataFrame
            columns: Specific columns to plot (if None, plots all numeric columns)
            
        Returns:
            Plotly box plot figure
        """
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if columns:
                numeric_cols = [col for col in columns if col in numeric_cols]
            
            fig = go.Figure()
            
            for col in numeric_cols:
                fig.add_trace(go.Box(
                    y=df[col],
                    name=col,
                    boxpoints='outliers'
                ))
            
            fig.update_layout(
                title="Box Plots - Distribution and Outliers",
                yaxis_title="Values",
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating box plot: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        color_col: Optional[str] = None, top_n: int = 20) -> go.Figure:
        """
        Create a bar chart.
        
        Args:
            df: Pandas DataFrame
            x_col: Column for x-axis (categories)
            y_col: Column for y-axis (values)
            color_col: Column for color coding (optional)
            top_n: Number of top categories to show
            
        Returns:
            Plotly bar chart figure
        """
        try:
            # Aggregate data if needed
            if df[x_col].dtype == 'object' and df[y_col].dtype in ['int64', 'float64']:
                plot_df = df.groupby(x_col)[y_col].sum().reset_index()
                plot_df = plot_df.nlargest(top_n, y_col)
            else:
                plot_df = df.head(top_n)
            
            fig = px.bar(
                plot_df, x=x_col, y=y_col,
                color=color_col,
                template=self.theme
            )
            
            fig.update_layout(
                title=f"{y_col} by {x_col}",
                xaxis_title=x_col,
                yaxis_title=y_col
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
    
    def suggest_best_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Suggest the best visualizations based on data characteristics.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of dictionaries with visualization suggestions
        """
        suggestions = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        date_cols = df.select_dtypes(include=['datetime']).columns
        
        # Convert object columns that might be dates
        for col in categorical_cols:
            try:
                pd.to_datetime(df[col], errors='raise')
                date_cols = date_cols.append(pd.Index([col]))
            except:
                pass
        
        # Correlation matrix for multiple numeric columns
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "correlation_matrix",
                "title": "Correlation Analysis",
                "description": "Shows relationships between numeric variables",
                "function": "create_correlation_matrix"
            })
        
        # Distribution plots for numeric columns
        if len(numeric_cols) > 0:
            suggestions.append({
                "type": "distribution",
                "title": "Data Distributions",
                "description": f"Distribution analysis for {len(numeric_cols)} numeric columns",
                "function": "create_distribution_plots"
            })
            
            # Box plots for outlier detection
            suggestions.append({
                "type": "box_plot",
                "title": "Outlier Detection",
                "description": "Box plots to identify outliers in numeric data",
                "function": "create_box_plot"
            })
        
        # Scatter plots for numeric pairs
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter",
                "title": "Scatter Plot Analysis",
                "description": f"Relationship between {numeric_cols[0]} and {numeric_cols[1]}",
                "x_col": numeric_cols[0],
                "y_col": numeric_cols[1],
                "function": "create_scatter_plot"
            })
        
        # Bar charts for categorical data
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "bar_chart",
                "title": "Category Analysis",
                "description": f"Analysis of {categorical_cols[0]} by {numeric_cols[0]}",
                "x_col": categorical_cols[0],
                "y_col": numeric_cols[0],
                "function": "create_bar_chart"
            })
        
        # Time series for date columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "time_series",
                "title": "Time Series Analysis",
                "description": f"Trends over time for {numeric_cols[0]}",
                "date_col": date_cols[0],
                "value_cols": list(numeric_cols[:3]),
                "function": "create_time_series_plot"
            })
        
        # Overview dashboard
        suggestions.append({
            "type": "overview",
            "title": "Data Overview Dashboard",
            "description": "Comprehensive overview of the dataset",
            "function": "create_overview_dashboard"
        })
        
        return suggestions
    
    def create_visualization_from_suggestion(self, df: pd.DataFrame, suggestion: Dict[str, Any]) -> go.Figure:
        """
        Create a visualization based on a suggestion dictionary.
        
        Args:
            df: Pandas DataFrame
            suggestion: Suggestion dictionary from suggest_best_visualizations
            
        Returns:
            Plotly figure
        """
        try:
            function_name = suggestion.get("function")
            
            if function_name == "create_correlation_matrix":
                return self.create_correlation_matrix(df)
            elif function_name == "create_distribution_plots":
                plots = self.create_distribution_plots(df)
                return plots[0] if plots else go.Figure()
            elif function_name == "create_box_plot":
                return self.create_box_plot(df)
            elif function_name == "create_scatter_plot":
                return self.create_scatter_plot(df, suggestion["x_col"], suggestion["y_col"])
            elif function_name == "create_bar_chart":
                return self.create_bar_chart(df, suggestion["x_col"], suggestion["y_col"])
            elif function_name == "create_time_series_plot":
                return self.create_time_series_plot(df, suggestion["date_col"], suggestion["value_cols"])
            elif function_name == "create_overview_dashboard":
                return self.create_overview_dashboard(df)
            else:
                return go.Figure().add_annotation(text="Unknown visualization type", x=0.5, y=0.5)
                
        except Exception as e:
            logger.error(f"Error creating visualization from suggestion: {str(e)}")
            return go.Figure().add_annotation(text=f"Error: {str(e)}", x=0.5, y=0.5)
