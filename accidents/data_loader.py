"""
Data loading utilities for the US Accidents package.
"""

import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional
import warnings


class DataLoader:
    """
    Handles data loading and validation for US Accidents dataset.
    
    This class provides efficient data loading using DuckDB for handling
    large datasets (7M+ records) that may not fit in memory.
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize the DataLoader.
        
        Args:
            data_path: Path to the US Accidents CSV file
        """
        self.data_path = Path(data_path)
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
    
    def load_to_duckdb(self, table_name: str = "accidents") -> duckdb.DuckDBPyConnection:
        """
        Load CSV data into DuckDB for efficient processing.
        
        Args:
            table_name: Name for the table in DuckDB
            
        Returns:
            DuckDB connection with loaded data
        """
        conn = duckdb.connect()
        
        try:
            # Load CSV into DuckDB with automatic schema detection
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{self.data_path}')
            """)
            
            print(f"✅ Data loaded successfully into DuckDB table '{table_name}'")
            return conn
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            conn.close()
            raise
    
    def load_sample(self, n_rows: int = 10000) -> pd.DataFrame:
        """
        Load a sample of the data for quick exploration.
        
        Args:
            n_rows: Number of rows to sample
            
        Returns:
            Pandas DataFrame with sampled data
        """
        conn = duckdb.connect()
        
        try:
            # Sample data using DuckDB
            sample_df = conn.execute(f"""
                SELECT * FROM read_csv_auto('{self.data_path}')
                USING SAMPLE {n_rows} ROWS
            """).fetchdf()
            
            return sample_df
            
        except Exception as e:
            print(f"❌ Error loading sample: {e}")
            raise
        finally:
            conn.close()
    
    def validate_data(self) -> dict:
        """
        Perform data validation and return summary statistics.
        
        Returns:
            Dictionary with validation results
        """
        conn = duckdb.connect()
        
        try:
            # Load data temporarily for validation
            conn.execute(f"""
                CREATE TEMPORARY TABLE temp_accidents AS 
                SELECT * FROM read_csv_auto('{self.data_path}')
            """)
            
            # Basic statistics
            total_rows = conn.execute("SELECT COUNT(*) FROM temp_accidents").fetchone()[0]
            
            # Check key columns
            key_columns = ['ID', 'Start_Time', 'State', 'Severity', 'Weather_Condition']
            validation_results = {
                'total_rows': total_rows,
                'missing_values': {},
                'data_types': {},
                'value_ranges': {}
            }
            
            # Get column information
            columns_info = conn.execute("DESCRIBE temp_accidents").fetchdf()
            
            for col in key_columns:
                if col in columns_info['column_name'].values:
                    # Missing values
                    missing = conn.execute(f"""
                        SELECT COUNT(*) FROM temp_accidents 
                        WHERE "{col}" IS NULL OR "{col}" = ''
                    """).fetchone()[0]
                    
                    validation_results['missing_values'][col] = {
                        'count': missing,
                        'percentage': (missing / total_rows) * 100
                    }
            
            # Specific validations
            # Date range
            try:
                date_range = conn.execute("""
                    SELECT MIN(Start_Time) as min_date, MAX(Start_Time) as max_date
                    FROM temp_accidents WHERE Start_Time IS NOT NULL
                """).fetchone()
                validation_results['date_range'] = date_range
            except:
                validation_results['date_range'] = None
            
            # Severity range
            try:
                severity_range = conn.execute("""
                    SELECT MIN(Severity) as min_sev, MAX(Severity) as max_sev,
                           COUNT(DISTINCT Severity) as unique_sev
                    FROM temp_accidents WHERE Severity IS NOT NULL
                """).fetchone()
                validation_results['severity_range'] = severity_range
            except:
                validation_results['severity_range'] = None
            
            # State count
            try:
                state_count = conn.execute("""
                    SELECT COUNT(DISTINCT State) as unique_states
                    FROM temp_accidents 
                    WHERE State IS NOT NULL AND State != ''
                """).fetchone()[0]
                validation_results['unique_states'] = state_count
            except:
                validation_results['unique_states'] = None
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            raise
        finally:
            conn.close()
    
    def get_column_info(self) -> pd.DataFrame:
        """
        Get information about all columns in the dataset.
        
        Returns:
            DataFrame with column information
        """
        conn = duckdb.connect()
        
        try:
            # Get column info without loading full dataset
            column_info = conn.execute(f"""
                DESCRIBE (SELECT * FROM read_csv_auto('{self.data_path}') LIMIT 1)
            """).fetchdf()
            
            return column_info
            
        except Exception as e:
            print(f"❌ Error getting column info: {e}")
            raise
        finally:
            conn.close()
    
    def estimate_memory_usage(self) -> dict:
        """
        Estimate memory usage for loading the full dataset.
        
        Returns:
            Dictionary with memory estimates
        """
        # Get file size
        file_size_mb = self.data_path.stat().st_size / (1024 * 1024)
        
        # Rough estimates (CSV is typically 2-3x larger than in-memory representation)
        estimated_memory_mb = file_size_mb / 2.5
        
        return {
            'file_size_mb': file_size_mb,
            'estimated_memory_mb': estimated_memory_mb,
            'recommended_approach': 'DuckDB' if estimated_memory_mb > 1000 else 'Pandas'
        }