"""
Visualization utilities for the US Accidents package.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional, Tuple
import warnings


class AccidentVisualizer:
    """
    Creates visualizations for accident data analysis.
    
    This class provides standardized visualization methods for different
    types of accident analysis including temporal, geographic, and risk patterns.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize the visualizer.
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        sns.set_palette("husl")
        
    def plot_temporal_trends(self, data: pd.DataFrame, 
                           x_col: str = 'year', 
                           y_col: str = 'total_accidents',
                           title: str = 'Accident Trends Over Time') -> plt.Figure:
        """
        Create temporal trend visualizations.
        
        Args:
            data: DataFrame with temporal data
            x_col: Column name for x-axis (time dimension)
            y_col: Column name for y-axis (accident counts)
            title: Chart title
            
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Main trend line
        ax1.plot(data[x_col], data[y_col], marker='o', linewidth=3, markersize=8)
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.set_xlabel(x_col.title())
        ax1.set_ylabel(y_col.replace('_', ' ').title())
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for x, y in zip(data[x_col], data[y_col]):
            ax1.annotate(f'{y:,.0f}', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=9)
        
        # Year-over-year change
        if len(data) > 1:
            yoy_change = data[y_col].pct_change() * 100
            colors = ['red' if x < 0 else 'green' for x in yoy_change[1:]]
            ax2.bar(data[x_col][1:], yoy_change[1:], color=colors, alpha=0.7)
            ax2.set_title('Year-over-Year Change (%)', fontweight='bold')
            ax2.set_xlabel(x_col.title())
            ax2.set_ylabel('Change (%)')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        return fig
    
    def plot_geographic_distribution(self, data: pd.DataFrame,
                                   state_col: str = 'State',
                                   value_col: str = 'total_accidents',
                                   top_n: int = 15) -> plt.Figure:
        """
        Create geographic distribution visualizations.
        
        Args:
            data: DataFrame with state-level data
            state_col: Column name for states
            value_col: Column name for values to plot
            top_n: Number of top states to show
            
        Returns:
            Matplotlib figure
        """
        # Get top states
        top_states = data.nlargest(top_n, value_col)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Horizontal bar chart
        ax1.barh(range(len(top_states)), top_states[value_col], color='skyblue')
        ax1.set_yticks(range(len(top_states)))
        ax1.set_yticklabels(top_states[state_col])
        ax1.set_xlabel(value_col.replace('_', ' ').title())
        ax1.set_title(f'Top {top_n} States by {value_col.replace("_", " ").title()}', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # 2. Distribution histogram
        ax2.hist(data[value_col], bins=20, color='lightcoral', alpha=0.7, edgecolor='black')
        ax2.set_xlabel(value_col.replace('_', ' ').title())
        ax2.set_ylabel('Number of States')
        ax2.set_title('Distribution Across States', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Top 10 pie chart
        top_10 = data.nlargest(10, value_col)
        ax3.pie(top_10[value_col], labels=top_10[state_col], autopct='%1.1f%%', startangle=90)
        ax3.set_title('Top 10 States Share', fontweight='bold')
        
        # 4. Cumulative distribution
        sorted_data = data.sort_values(value_col, ascending=False)
        cumulative_pct = (sorted_data[value_col].cumsum() / sorted_data[value_col].sum() * 100)
        ax4.plot(range(1, len(cumulative_pct)+1), cumulative_pct.values, marker='o', linewidth=2)
        ax4.set_xlabel('Number of States (Ranked)')
        ax4.set_ylabel('Cumulative % of Total')
        ax4.set_title('Concentration Curve', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_severity_analysis(self, data: pd.DataFrame) -> plt.Figure:
        """
        Create severity analysis visualizations.
        
        Args:
            data: DataFrame with severity data over time
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Overall severity distribution
        overall_severity = data.groupby('Severity')['accident_count'].sum()
        colors = ['#90EE90', '#FFD700', '#FFA500', '#FF6347']
        
        axes[0,0].pie(overall_severity.values, 
                     labels=[f'Severity {s}' for s in overall_severity.index],
                     autopct='%1.1f%%', startangle=90, colors=colors)
        axes[0,0].set_title('Overall Severity Distribution', fontweight='bold')
        
        # Severity trends over time
        severity_pivot = data.pivot(index='year', columns='Severity', values='accident_count')
        for severity in severity_pivot.columns:
            axes[0,1].plot(severity_pivot.index, severity_pivot[severity], 
                          marker='o', linewidth=2, label=f'Severity {severity}')
        axes[0,1].set_title('Severity Trends Over Time', fontweight='bold')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Number of Accidents')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Severity percentages over time
        severity_pct = data.pivot(index='year', columns='Severity', values='percentage')
        axes[1,0].stackplot(severity_pct.index, 
                           severity_pct[1], severity_pct[2], 
                           severity_pct[3], severity_pct[4],
                           labels=['Severity 1', 'Severity 2', 'Severity 3', 'Severity 4'],
                           colors=colors, alpha=0.8)
        axes[1,0].set_title('Severity Distribution Over Time (%)', fontweight='bold')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Percentage')
        axes[1,0].legend(loc='upper right')
        axes[1,0].set_ylim(0, 100)
        
        # Year-over-year changes
        severity_changes = severity_pivot.pct_change() * 100
        severity_changes = severity_changes.dropna()
        
        x = range(len(severity_changes))
        width = 0.2
        for i, severity in enumerate(severity_changes.columns):
            axes[1,1].bar([pos + width*i for pos in x], severity_changes[severity], 
                         width, label=f'Severity {severity}', alpha=0.8)
        
        axes[1,1].set_title('Year-over-Year Changes (%)', fontweight='bold')
        axes[1,1].set_xlabel('Year')
        axes[1,1].set_ylabel('Change (%)')
        axes[1,1].set_xticks([pos + width*1.5 for pos in x])
        axes[1,1].set_xticklabels([f'{year:.0f}' for year in severity_changes.index])
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3, axis='y')
        axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        return fig
    
    def plot_time_patterns(self, temporal_data: Dict[str, pd.DataFrame]) -> plt.Figure:
        """
        Create comprehensive time pattern visualizations.
        
        Args:
            temporal_data: Dictionary with 'hourly', 'daily', 'monthly', 'seasonal' DataFrames
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Hourly patterns
        if 'hourly' in temporal_data:
            hourly = temporal_data['hourly']
            bars = axes[0,0].bar(hourly['hour'], hourly['accident_count'], 
                               color='skyblue', alpha=0.8, edgecolor='navy')
            axes[0,0].set_title('Accidents by Hour of Day', fontweight='bold')
            axes[0,0].set_xlabel('Hour (24-hour format)')
            axes[0,0].set_ylabel('Number of Accidents')
            axes[0,0].grid(True, alpha=0.3, axis='y')
            
            # Highlight peak hour
            max_hour_idx = hourly['accident_count'].idxmax()
            bars[max_hour_idx].set_color('red')
        
        # Daily patterns
        if 'daily' in temporal_data:
            daily = temporal_data['daily']
            dow_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            daily['day_name'] = [dow_names[int(d)] for d in daily['day_of_week']]
            
            bars = axes[0,1].bar(daily['day_name'], daily['accident_count'], 
                               color='lightgreen', alpha=0.8, edgecolor='darkgreen')
            axes[0,1].set_title('Accidents by Day of Week', fontweight='bold')
            axes[0,1].set_xlabel('Day of Week')
            axes[0,1].set_ylabel('Number of Accidents')
            axes[0,1].tick_params(axis='x', rotation=45)
            axes[0,1].grid(True, alpha=0.3, axis='y')
            
            # Highlight weekends
            weekend_indices = [0, 6]  # Sunday, Saturday
            for i in weekend_indices:
                if i < len(bars):
                    bars[i].set_color('purple')
        
        # Monthly patterns
        if 'monthly' in temporal_data:
            monthly = temporal_data['monthly']
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            monthly['month_name'] = [month_names[int(m)-1] for m in monthly['month']]
            
            bars = axes[1,0].bar(monthly['month_name'], monthly['accident_count'], 
                               color='lightcoral', alpha=0.8, edgecolor='darkred')
            axes[1,0].set_title('Accidents by Month', fontweight='bold')
            axes[1,0].set_xlabel('Month')
            axes[1,0].set_ylabel('Number of Accidents')
            axes[1,0].tick_params(axis='x', rotation=45)
            axes[1,0].grid(True, alpha=0.3, axis='y')
            
            # Highlight peak month
            max_month_idx = monthly['accident_count'].idxmax()
            bars[max_month_idx].set_color('red')
        
        # Seasonal patterns
        if 'seasonal' in temporal_data:
            seasonal = temporal_data['seasonal']
            axes[1,1].pie(seasonal['accident_count'], labels=seasonal['season'], 
                         autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
            axes[1,1].set_title('Accidents by Season', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def create_interactive_state_trends(self, data: pd.DataFrame, 
                                      top_n: int = 10) -> go.Figure:
        """
        Create interactive state trends using Plotly.
        
        Args:
            data: DataFrame with state-year-accidents data
            top_n: Number of top states to include
            
        Returns:
            Plotly figure
        """
        # Get top states
        top_states = (data.groupby('State')['total_accidents']
                     .sum().nlargest(top_n).index.tolist())
        
        filtered_data = data[data['State'].isin(top_states)]
        
        fig = px.line(filtered_data, 
                     x='year', 
                     y='total_accidents', 
                     color='State',
                     title=f'Interactive: Accident Trends by State (Top {top_n})',
                     labels={'total_accidents': 'Number of Accidents', 'year': 'Year'},
                     height=600,
                     line_shape='spline')
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title='Year',
            yaxis_title='Number of Accidents',
            legend_title='State',
            font=dict(size=12),
            title_font_size=16
        )
        
        return fig
    
    def create_weather_heatmap(self, weather_data: pd.DataFrame,
                             top_states: int = 10,
                             top_weather: int = 8) -> plt.Figure:
        """
        Create weather conditions heatmap.
        
        Args:
            weather_data: DataFrame with State, Weather_Condition, accident_count
            top_states: Number of top states to include
            top_weather: Number of top weather conditions to include
            
        Returns:
            Matplotlib figure
        """
        # Get top states and weather conditions
        top_states_list = (weather_data.groupby('State')['accident_count']
                          .sum().nlargest(top_states).index.tolist())
        
        top_weather_list = (weather_data.groupby('Weather_Condition')['accident_count']
                           .sum().nlargest(top_weather).index.tolist())
        
        # Filter data
        filtered_data = weather_data[
            (weather_data['State'].isin(top_states_list)) &
            (weather_data['Weather_Condition'].isin(top_weather_list))
        ]
        
        # Create pivot table
        heatmap_data = filtered_data.pivot_table(
            values='accident_count', 
            index='State', 
            columns='Weather_Condition', 
            fill_value=0
        )
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sns.heatmap(heatmap_data, 
                   annot=True, 
                   fmt='.0f', 
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Number of Accidents'},
                   ax=ax)
        
        ax.set_title('Weather Conditions vs States Heatmap', fontweight='bold', fontsize=16)
        ax.set_xlabel('Weather Condition', fontsize=12)
        ax.set_ylabel('State', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig
    
    def save_figure(self, fig: plt.Figure, filename: str, 
                   output_dir: str = 'outputs', dpi: int = 300):
        """
        Save figure to file.
        
        Args:
            fig: Matplotlib figure to save
            filename: Output filename
            output_dir: Output directory
            dpi: Resolution for saved figure
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        full_path = output_path / filename
        fig.savefig(full_path, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"✅ Figure saved: {full_path}")
    
    @staticmethod
    def setup_plotly_theme():
        """Set up consistent Plotly theme."""
        import plotly.io as pio
        
        # Set default template
        pio.templates.default = "plotly_white"
        
        # Custom color palette
        custom_colors = [
            '#2E86AB', '#A23B72', '#F18F01', '#C73E1D',
            '#593E2C', '#4B5842', '#8D5A97', '#F4B942'
        ]
        
        return custom_colors