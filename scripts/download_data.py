#!/usr/bin/env python3
"""
Script to download US Accidents dataset from Kaggle
"""
import os
import sys
from pathlib import Path
import zipfile

try:
    import kaggle
except ImportError:
    print("Error: kaggle package not installed. Run: pip install kaggle")
    sys.exit(1)

def download_accidents_data():
    """Download US Accidents dataset from Kaggle"""
    
    # Create data directory
    data_dir = Path("../data")
    data_dir.mkdir(exist_ok=True)
    
    print("Starting download of US Accidents dataset...")
    
    try:
        # Download dataset - this will download a zip file
        kaggle.api.dataset_download_files(
            'sobhanmoosavi/us-accidents',
            path=str(data_dir),
            unzip=True
        )
        print("Dataset downloaded and extracted successfully!")
        
        # List files in data directory
        print("\nFiles in data directory:")
        for file in data_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  {file.name} ({size_mb:.1f} MB)")
                
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("Make sure you have:")
        print("1. Kaggle API token in ~/.kaggle/kaggle.json")
        print("2. Accepted the dataset terms on Kaggle website")
        return False
    
    return True

if __name__ == "__main__":
    success = download_accidents_data()
    if success:
        print("\n✅ Download completed successfully!")
    else:
        print("\n❌ Download failed!")
        sys.exit(1)