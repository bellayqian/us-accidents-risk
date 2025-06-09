"""
Core risk analysis functionality for the US Accidents package.
"""

import pandas as pd
import duckdb
from pathlib import Path
from typing import List, Dict, Optional, Union
import warnings

from .data_loader import DataLoader


class RiskAnalyzer:
    """
    Main class for analyzing accident risk patterns.
    
    This class provides methods to compute various risk metrics from US accident data,
    including state-level rates, temporal patterns, and multi-dimensional analysis.
    
    Example:
        analyzer = RiskAnalyzer(data_path='data/US_Accidents.csv')
        risk_metrics = analyzer.compute_risk(levels=['State', 'Severity'])
    """
    
    def __init__(self, data_path: Union[str, Path]):
        """
        Initialize the RiskAnalyzer.
        
        Args:
            data_path: Path to the US Accidents CSV file
        """
        self.data_path = Path(data_path)
        self.data_loader = DataLoader(self.data_path)
        self.conn = None
        self._data_loaded = False
        
    def _ensure_data_loaded(self):
        """Ensure data is loaded into DuckDB."""
        if not self._data_loaded:
            self.conn = self.data_loader.load_to_duckdb()
            self._data_loaded = True
            
    def compute_risk(self, levels: List[str], 
                    include_weather: bool = True,
                    include_time: bool = True) -> pd.DataFrame:
        """
        Compute risk metrics at specified aggregation levels.
        
        Args:
            levels: List of columns to group by (e.g., ['State', 'Severity'])
            include_weather: Whether to include weather conditions
            include_time: Whether to include temporal dimensions
            
        Returns:
            DataFrame with computed risk metrics
        """
        self._ensure_data_loaded()
        
        # Build the grouping columns
        group_cols = ['EXTRACT(year FROM Start_Time::TIMESTAMP) as year'] + levels
        
        if include_weather and 'Weather_Condition' not in levels:
            group_cols.append('Weather_Condition')
            
        if include_time:
            group_cols.extend([
                'EXTRACT(month FROM Start_Time::TIMESTAMP) as month',
                'EXTRACT(hour FROM Start_Time::TIMESTAMP) as hour'
            ])
        
        # Build the query
        select_cols = ', '.join(group_cols)
        group_by_cols = ', '.join([col.split(' as ')[-1] for col in group_cols])
        
        query = f"""
        SELECT 
            {select_cols},
            COUNT(*) as accident_count,
            AVG(Severity) as avg_severity
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND State IS NOT NULL AND State != ''
            AND Severity IS NOT NULL
        GROUP BY {group_by_cols}
        ORDER BY year, accident_count DESC
        """
        
        return self.conn.execute(query).fetchdf()
    
    def compute_state_risk_rates(self) -> pd.DataFrame:
        """
        Compute annual accident rates by state.
        
        Returns:
            DataFrame with state-level annual accident rates
        """
        self._ensure_data_loaded()
        
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            State,
            COUNT(*) as total_accidents,
            COUNT(CASE WHEN Severity >= 3 THEN 1 END) as severe_accidents,
            COUNT(CASE WHEN Severity >= 3 THEN 1 END) * 100.0 / COUNT(*) as severe_accident_rate
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND State IS NOT NULL AND State != ''
            AND Severity IS NOT NULL
        GROUP BY year, State
        ORDER BY year, total_accidents DESC
        """
        
        return self.conn.execute(query).fetchdf()
    
    def compute_temporal_patterns(self) -> Dict[str, pd.DataFrame]:
        """
        Compute comprehensive temporal accident patterns.
        
        Returns:
            Dictionary containing different temporal analyses:
            - 'hourly': Accidents by hour of day
            - 'daily': Accidents by day of week  
            - 'monthly': Accidents by month
            - 'seasonal': Accidents by season
        """
        self._ensure_data_loaded()
        
        patterns = {}
        
        # Hourly patterns
        patterns['hourly'] = self.conn.execute("""
            SELECT 
                EXTRACT(hour FROM Start_Time::TIMESTAMP) as hour,
                COUNT(*) as accident_count,
                AVG(Severity) as avg_severity
            FROM accidents 
            WHERE Start_Time IS NOT NULL
            GROUP BY hour
            ORDER BY hour
        """).fetchdf()
        
        # Daily patterns
        patterns['daily'] = self.conn.execute("""
            SELECT 
                EXTRACT(dow FROM Start_Time::TIMESTAMP) as day_of_week,
                COUNT(*) as accident_count,
                AVG(Severity) as avg_severity
            FROM accidents 
            WHERE Start_Time IS NOT NULL
            GROUP BY day_of_week
            ORDER BY day_of_week
        """).fetchdf()
        
        # Monthly patterns
        patterns['monthly'] = self.conn.execute("""
            SELECT 
                EXTRACT(month FROM Start_Time::TIMESTAMP) as month,
                COUNT(*) as accident_count,
                AVG(Severity) as avg_severity
            FROM accidents 
            WHERE Start_Time IS NOT NULL
            GROUP BY month
            ORDER BY month
        """).fetchdf()
        
        # Seasonal patterns
        patterns['seasonal'] = self.conn.execute("""
            SELECT 
                CASE 
                    WHEN EXTRACT(month FROM Start_Time::TIMESTAMP) IN (12, 1, 2) THEN 'Winter'
                    WHEN EXTRACT(month FROM Start_Time::TIMESTAMP) IN (3, 4, 5) THEN 'Spring'
                    WHEN EXTRACT(month FROM Start_Time::TIMESTAMP) IN (6, 7, 8) THEN 'Summer'
                    WHEN EXTRACT(month FROM Start_Time::TIMESTAMP) IN (9, 10, 11) THEN 'Fall'
                END as season,
                COUNT(*) as accident_count,
                AVG(Severity) as avg_severity
            FROM accidents 
            WHERE Start_Time IS NOT NULL
            GROUP BY season
            ORDER BY accident_count DESC
        """).fetchdf()
        
        return patterns
    
    def compute_weather_risk(self) -> pd.DataFrame:
        """
        Compute accident risk by weather conditions and state.
        
        Returns:
            DataFrame with weather-based risk analysis
        """
        self._ensure_data_loaded()
        
        query = """
        SELECT 
            State,
            Weather_Condition,
            COUNT(*) as accident_count,
            AVG(Severity) as avg_severity,
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY State) as state_percentage,
            ROW_NUMBER() OVER (PARTITION BY State ORDER BY COUNT(*) DESC) as weather_rank
        FROM accidents 
        WHERE State IS NOT NULL AND State != ''
            AND Weather_Condition IS NOT NULL AND Weather_Condition != ''
            AND Severity IS NOT NULL
        GROUP BY State, Weather_Condition
        ORDER BY State, accident_count DESC
        """
        
        return self.conn.execute(query).fetchdf()
    
    def generate_summary_report(self) -> Dict[str, any]:
        """
        Generate a comprehensive summary report of the dataset.
        
        Returns:
            Dictionary containing summary statistics and insights
        """
        self._ensure_data_loaded()
        
        # Basic statistics
        total_accidents = self.conn.execute("SELECT COUNT(*) FROM accidents").fetchone()[0]
        
        date_range = self.conn.execute("""
            SELECT MIN(Start_Time) as min_date, MAX(Start_Time) as max_date
            FROM accidents WHERE Start_Time IS NOT NULL
        """).fetchone()
        
        state_count = self.conn.execute("""
            SELECT COUNT(DISTINCT State) as states
            FROM accidents WHERE State IS NOT NULL AND State != ''
        """).fetchone()[0]
        
        # Top states
        top_states = self.conn.execute("""
            SELECT State, COUNT(*) as accidents
            FROM accidents 
            WHERE State IS NOT NULL AND State != ''
            GROUP BY State 
            ORDER BY accidents DESC 
            LIMIT 10
        """).fetchdf()
        
        # Severity distribution
        severity_dist = self.conn.execute("""
            SELECT Severity, COUNT(*) as count,
                   COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
            FROM accidents 
            WHERE Severity IS NOT NULL
            GROUP BY Severity 
            ORDER BY Severity
        """).fetchdf()
        
        return {
            'total_accidents': total_accidents,
            'date_range': date_range,
            'states_covered': state_count,
            'top_states': top_states,
            'severity_distribution': severity_dist
        }
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self._data_loaded = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()