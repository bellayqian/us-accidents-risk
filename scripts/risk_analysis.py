#!/usr/bin/env python3
"""
Risk analysis script for US Accidents dataset
Computes annual state-level accident rates stratified by severity and weather
"""
import duckdb
import pandas as pd
from pathlib import Path
import sys

class RiskAnalyzer:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        self.conn = duckdb.connect()
        self._load_data()
    
    def _load_data(self):
        """Load data into DuckDB"""
        print("Loading data for risk analysis...")
        self.conn.execute(f"""
            CREATE TABLE accidents AS 
            SELECT * FROM read_csv_auto('{self.data_path}')
        """)
        print("✅ Data loaded!")
    
    def compute_risk_metrics(self):
        """Compute annual state-level accident rates"""
        print("Computing risk metrics...")
        
        # Main risk metrics query
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            State,
            Severity,
            Weather_Condition,
            COUNT(*) as accident_count
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND State IS NOT NULL
            AND State != ''
            AND Severity IS NOT NULL
            AND Weather_Condition IS NOT NULL 
            AND Weather_Condition != ''
            AND Weather_Condition != 'Unknown'
        GROUP BY year, State, Severity, Weather_Condition
        ORDER BY year, State, accident_count DESC
        """
        
        risk_metrics = self.conn.execute(query).fetchdf()
        print(f"✅ Computed risk metrics: {len(risk_metrics):,} records")
        return risk_metrics
    
    def compute_detailed_risk_metrics(self):
        """Compute risk metrics including time of day stratification"""
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            State,
            Severity,
            Weather_Condition,
            CASE 
                WHEN EXTRACT(hour FROM Start_Time::TIMESTAMP) BETWEEN 6 AND 11 THEN 'Morning'
                WHEN EXTRACT(hour FROM Start_Time::TIMESTAMP) BETWEEN 12 AND 17 THEN 'Afternoon'  
                WHEN EXTRACT(hour FROM Start_Time::TIMESTAMP) BETWEEN 18 AND 21 THEN 'Evening'
                ELSE 'Night'
            END as time_of_day,
            COUNT(*) as accident_count
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND State IS NOT NULL AND State != ''
            AND Severity IS NOT NULL
            AND Weather_Condition IS NOT NULL AND Weather_Condition != ''
        GROUP BY year, State, Severity, Weather_Condition, time_of_day
        ORDER BY year, State, accident_count DESC
        """
        return self.conn.execute(query).fetchdf()

    def compute_annual_state_totals(self):
        """Compute total accidents per state per year"""
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            State,
            COUNT(*) as total_accidents
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND State IS NOT NULL
            AND State != ''
        GROUP BY year, State
        ORDER BY year, total_accidents DESC
        """
        
        return self.conn.execute(query).fetchdf()
    
    def compute_severity_trends(self):
        """Compute severity trends by year"""
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            Severity,
            COUNT(*) as accident_count,
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY EXTRACT(year FROM Start_Time::TIMESTAMP)) as percentage
        FROM accidents 
        WHERE Start_Time IS NOT NULL 
            AND Severity IS NOT NULL
        GROUP BY year, Severity
        ORDER BY year, Severity
        """
        
        return self.conn.execute(query).fetchdf()
    
    def compute_weather_by_state(self):
        """Compute most common weather conditions per state"""
        query = """
        WITH weather_counts AS (
            SELECT 
                State,
                Weather_Condition,
                COUNT(*) as accident_count,
                ROW_NUMBER() OVER (PARTITION BY State ORDER BY COUNT(*) DESC) as rn
            FROM accidents 
            WHERE State IS NOT NULL 
                AND State != ''
                AND Weather_Condition IS NOT NULL
                AND Weather_Condition != ''
            GROUP BY State, Weather_Condition
        )
        SELECT 
            State,
            Weather_Condition,
            accident_count
        FROM weather_counts 
        WHERE rn <= 5  -- Top 5 weather conditions per state
        ORDER BY State, accident_count DESC
        """
        
        return self.conn.execute(query).fetchdf()
    
    def compute_time_patterns(self):
        """Compute accident patterns by time of day and day of week"""
        query = """
        SELECT 
            EXTRACT(year FROM Start_Time::TIMESTAMP) as year,
            EXTRACT(month FROM Start_Time::TIMESTAMP) as month,
            EXTRACT(hour FROM Start_Time::TIMESTAMP) as hour,
            EXTRACT(dow FROM Start_Time::TIMESTAMP) as day_of_week,  -- 0=Sunday, 6=Saturday
            COUNT(*) as accident_count
        FROM accidents 
        WHERE Start_Time IS NOT NULL
        GROUP BY year, month, hour, day_of_week
        ORDER BY year, month, hour
        """
        
        return self.conn.execute(query).fetchdf()
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*60)
        print("RISK ANALYSIS SUMMARY REPORT")
        print("="*60)
        
        # Overall statistics
        total_accidents = self.conn.execute("SELECT COUNT(*) FROM accidents").fetchone()[0]
        print(f"Total accidents in dataset: {total_accidents:,}")
        
        # Year range
        year_range = self.conn.execute("""
            SELECT MIN(EXTRACT(year FROM Start_Time::TIMESTAMP)) as min_year,
                   MAX(EXTRACT(year FROM Start_Time::TIMESTAMP)) as max_year
            FROM accidents WHERE Start_Time IS NOT NULL
        """).fetchone()
        print(f"Data covers: {int(year_range[0])} - {int(year_range[1])}")
        
        # Top 10 states by total accidents
        print(f"\nTop 10 states by total accidents:")
        top_states = self.conn.execute("""
            SELECT State, COUNT(*) as total_accidents
            FROM accidents 
            WHERE State IS NOT NULL AND State != ''
            GROUP BY State 
            ORDER BY total_accidents DESC 
            LIMIT 10
        """).fetchdf()
        
        for idx, row in top_states.iterrows():
            print(f"  {idx+1:2d}. {row['State']}: {row['total_accidents']:,}")
        
        # Severity distribution
        print(f"\nSeverity distribution:")
        severity_dist = self.conn.execute("""
            SELECT Severity, COUNT(*) as count, 
                   COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
            FROM accidents 
            WHERE Severity IS NOT NULL
            GROUP BY Severity 
            ORDER BY Severity
        """).fetchdf()
        
        for idx, row in severity_dist.iterrows():
            print(f"  Severity {int(row['Severity'])}: {int(row['count']):,} ({row['percentage']:.1f}%)")
    
    def save_results(self, output_dir="../data/processed"):
        """Save all computed metrics to CSV files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\nSaving results to {output_path}...")
        
        # Compute and save all metrics
        metrics = {
            'risk_metrics': self.compute_risk_metrics(),
            'detailed_risk_metrics': self.compute_detailed_risk_metrics(),
            'annual_state_totals': self.compute_annual_state_totals(),
            'severity_trends': self.compute_severity_trends(),
            'weather_by_state': self.compute_weather_by_state(),
            'time_patterns': self.compute_time_patterns()
        }
        
        for name, df in metrics.items():
            file_path = output_path / f"{name}.csv"
            df.to_csv(file_path, index=False)
            print(f"  Saved {name}: {len(df):,} records -> {file_path}")
        
        return metrics
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    # Look for the CSV file in the data directory
    data_dir = Path("../data")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in ../data directory")
        print("Make sure you've run download_data.py first")
        return
    
    # Use the first CSV file found
    data_file = csv_files[0]
    print(f"Analyzing file: {data_file}")
    
    # Initialize analyzer
    analyzer = RiskAnalyzer(data_file)
    
    try:
        # Generate summary report
        analyzer.generate_summary_report()
        
        # Save detailed results
        results = analyzer.save_results()
        
        print(f"\n✅ Risk analysis completed successfully!")
        print(f"   Results saved to ../data/processed/")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()