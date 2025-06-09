#!/usr/bin/env python3
"""
Data processing script for US Accidents dataset
Handles large data using DuckDB for memory efficiency
"""
import duckdb
import pandas as pd
from pathlib import Path
import sys

class AccidentsDataProcessor:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        # Initialize DuckDB connection
        self.conn = duckdb.connect()
        print(f"Initialized processor for: {self.data_path}")
    
    def load_and_validate(self):
        """Load data and perform integrity checks"""
        print("Loading data into DuckDB...")
        
        try:
            # Load CSV into DuckDB - this handles large files efficiently
            self.conn.execute(f"""
                CREATE TABLE accidents AS 
                SELECT * FROM read_csv_auto('{self.data_path}')
            """)
            print("✅ Data loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        # Basic integrity checks
        self._perform_integrity_checks()
        return True
    
    def _perform_integrity_checks(self):
        """Perform basic data integrity checks"""
        print("\n📊 Data Integrity Report:")
        print("=" * 40)
        
        # Total records
        total_rows = self.conn.execute("SELECT COUNT(*) FROM accidents").fetchone()[0]
        print(f"Total records: {total_rows:,}")
        
        # Check column info
        columns_info = self.conn.execute("""
            DESCRIBE accidents
        """).fetchdf()
        print(f"Total columns: {len(columns_info)}")
        
        # Check missing values in key columns
        key_columns = ['ID', 'Start_Time', 'State', 'Severity', 'Weather_Condition']
        print(f"\nMissing values in key columns:")
        
        for col in key_columns:
            try:
                missing = self.conn.execute(f"""
                    SELECT COUNT(*) FROM accidents 
                    WHERE "{col}" IS NULL OR "{col}" = ''
                """).fetchone()[0]
                missing_pct = (missing / total_rows) * 100
                print(f"  {col}: {missing:,} ({missing_pct:.1f}%)")
            except Exception as e:
                print(f"  {col}: Error checking - {e}")
        
        # Check data types and ranges
        self._check_data_ranges()
    
    def _check_data_ranges(self):
        """Check data ranges for key columns"""
        print(f"\nData ranges:")
        
        # Severity range
        try:
            severity_range = self.conn.execute("""
                SELECT MIN(Severity) as min_sev, MAX(Severity) as max_sev, 
                       COUNT(DISTINCT Severity) as unique_sev
                FROM accidents 
                WHERE Severity IS NOT NULL
            """).fetchone()
            print(f"  Severity: {severity_range[0]} to {severity_range[1]} ({severity_range[2]} unique values)")
        except:
            print("  Severity: Error checking range")
        
        # Date range
        try:
            date_range = self.conn.execute("""
                SELECT MIN(Start_Time) as min_date, MAX(Start_Time) as max_date
                FROM accidents 
                WHERE Start_Time IS NOT NULL
            """).fetchone()
            print(f"  Date range: {date_range[0]} to {date_range[1]}")
        except:
            print("  Date range: Error checking range")
        
        # State count
        try:
            state_count = self.conn.execute("""
                SELECT COUNT(DISTINCT State) as unique_states
                FROM accidents 
                WHERE State IS NOT NULL AND State != ''
            """).fetchone()[0]
            print(f"  Unique states: {state_count}")
        except:
            print("  States: Error checking count")
    
    def get_sample_data(self, n=5):
        """Get a sample of the data for inspection"""
        return self.conn.execute(f"""
            SELECT ID, Start_Time, State, Severity, Weather_Condition
            FROM accidents 
            LIMIT {n}
        """).fetchdf()
    
    def get_column_names(self):
        """Get all column names"""
        return self.conn.execute("DESCRIBE accidents").fetchdf()['column_name'].tolist()
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

def main():
    # Look for the CSV file in the data directory
    data_dir = Path("../data")
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in ../data directory")
        print("Make sure you've run download_data.py first")
        return
    
    # Use the first CSV file found (should be US_Accidents*.csv)
    data_file = csv_files[0]
    print(f"Processing file: {data_file}")
    
    # Initialize processor
    processor = AccidentsDataProcessor(data_file)
    
    # Load and validate data
    if processor.load_and_validate():
        print("\n📋 Sample data:")
        sample = processor.get_sample_data()
        print(sample.to_string())
        
        print(f"\n📋 Available columns:")
        columns = processor.get_column_names()
        for i, col in enumerate(columns, 1):
            print(f"  {i:2d}. {col}")
    
    processor.close()

if __name__ == "__main__":
    main()