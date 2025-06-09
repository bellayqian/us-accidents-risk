# US Accidents Risk Analysis

A comprehensive analysis of traffic accident patterns and public health risks using the US Accidents dataset (2016-2023) from Kaggle.

## Dataset Description

This project analyzes the **US Accidents (2016-2023)** dataset, which contains approximately **7.7 million** accident records across **49 US states**. The data was collected from multiple APIs that provide streaming traffic incident data from:

- US and state departments of transportation
- Law enforcement agencies  
- Traffic cameras and sensors
- Various traffic monitoring entities

**Dataset Source**: [Kaggle - US Accidents Dataset](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)

**Purpose**: This repository provides a comprehensive risk analysis framework for understanding traffic accident patterns, identifying high-risk conditions, and supporting public health decision-making through data-driven insights.

## Project Structure

```
us-accidents-risk/
├── accidents/                  # Main Python package
│   ├── __init__.py            # Package initialization
│   ├── analyzer.py            # Core RiskAnalyzer class
│   ├── cli.py                 # Command-line interface
│   ├── data_loader.py         # Data loading utilities
│   └── visualizations.py     # Visualization tools
├── data/                      # Data directory (excluded from git)
│   ├── US_Accidents_March23.csv  # Raw dataset
│   └── processed/             # Processed analysis results
├── scripts/                   # Data processing scripts
│   ├── download_data.py       # Kaggle dataset download
│   ├── data_processing.py     # Data loading and validation
│   └── risk_analysis.py       # Risk metrics computation
├── notebooks/                 # Jupyter notebooks
│   └── eda.ipynb             # Exploratory data analysis
├── examples/                  # Package usage examples
│   └── example_usage.py       # Comprehensive examples
├── setup.py                   # Package installation config
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## System Requirements

### Python Version
- **Required**: Python 3.8 or higher
- **Recommended**: Python 3.9 or 3.10 for optimal performance
- **Tested on**: Python 3.8, 3.9, 3.10, 3.11

### Dependencies

#### Core Dependencies (automatically installed)
```
pandas>=1.3.0          # Data manipulation and analysis
numpy>=1.21.0          # Numerical computing
duckdb>=0.8.0          # High-performance analytical database
matplotlib>=3.5.0      # Static visualizations  
seaborn>=0.11.0        # Statistical data visualization
plotly>=5.0.0          # Interactive visualizations
kaggle>=1.5.0          # Dataset download API
```

#### Development Dependencies (optional)
```
jupyter>=1.0.0         # Notebook environment
ipykernel>=6.0.0       # Jupyter kernel
pytest>=6.0.0          # Testing framework
black>=21.0.0          # Code formatting
```

#### System Requirements
- **Memory**: Minimum 8GB RAM (16GB recommended for full dataset)
- **Storage**: 5GB free space for dataset and processed files
- **Network**: Internet connection for initial data download

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Kaggle account and API token

### 1. Clone the Repository
```bash
git clone https://github.com/bellayqian/us-accidents-risk.git
cd us-accidents-risk
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Kaggle API
1. Create a Kaggle account and go to Account → API → "Create New API Token"
2. Download the `kaggle.json` file
3. Place it in the correct location:
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   ```

### 5. Install Package (Bonus Feature)
```bash
# Install as editable package for development
pip install -e .
```

## Usage

### Quick Start
```bash
# 1. Download dataset
cd scripts
python download_data.py

# 2. Process and validate data
python data_processing.py

# 3. Compute risk metrics
python risk_analysis.py

# 4. Run exploratory analysis
cd ../notebooks
jupyter notebook eda.ipynb
```

### Detailed Steps

#### 1. Download Dataset
```bash
cd scripts
python download_data.py
```
Downloads and extracts the US Accidents dataset to the `data/` directory (requires Kaggle API setup).

#### 2. Process and Validate Data  
```bash
python data_processing.py
```
- Loads 7.7M+ records using DuckDB for memory efficiency
- Performs data integrity checks and validation
- Provides comprehensive dataset overview

#### 3. Compute Risk Metrics
```bash
python risk_analysis.py
```
Computes comprehensive risk metrics including:
- Annual state-level accident rates stratified by severity and weather
- Time pattern analysis (hourly, daily, monthly, seasonal)
- Geographic risk distribution
- Results saved to `data/processed/` for fast loading

#### 4. Exploratory Data Analysis
```bash
cd ../notebooks
jupyter notebook eda.ipynb
```
Comprehensive EDA notebook featuring:
- ✅ **Accident rates over time** (temporal trends and patterns)
- ✅ **Most common weather conditions per state** (geographic weather analysis)
- ✅ **Severity trends by year** (accident severity evolution)
- 15+ interactive and static visualizations
- Multi-dimensional risk analysis

#### 5. (Bonus) Use as Python Package
```python
from accidents import RiskAnalyzer

analyzer = RiskAnalyzer(data_path='data/US_Accidents_March23.csv')
results = analyzer.compute_risk(levels=['State', 'Severity'])
print(f"Generated {len(results):,} risk records")
analyzer.close()
```

### Command Line Interface
```bash
# After package installation
accidents-analyze --data data/US_Accidents_March23.csv --analysis all
accidents-analyze --help  # For all options
```

## Assignment Compliance

This project fulfills all requirements from the homework assignment:

### ✅ Core Requirements
1. **Repository Setup**: Private GitHub repo with GitFlow branching
2. **Data Download**: Automated Kaggle API integration
3. **Large Data Handling**: DuckDB for memory-efficient processing
4. **Risk Metrics**: State-level accident rates with stratification
5. **EDA & Visualization**: 
   - Accident rates over time
   - Weather conditions per state  
   - Severity trends by year
   - 15+ visualizations using matplotlib, seaborn, plotly
6. **Documentation**: Comprehensive README with installation instructions

### ✅ Bonus Feature
**Python Package**: Reusable library with pip installation
```python
from accidents import RiskAnalyzer
analyzer = RiskAnalyzer(data_path='data/US_Accidents.csv')
analyzer.compute_risk(levels=['State', 'Severity'])
```

## Key Features

### 🔧 Technical Features
- **Large Data Handling**: Uses DuckDB for memory-efficient processing of 7.7M+ records
- **Data Integrity**: Comprehensive validation and quality checks
- **Modular Design**: Separate scripts for different analysis phases
- **Interactive Visualizations**: Plotly and matplotlib charts
- **Package Distribution**: Installable Python package with CLI

### 📊 Analysis Capabilities
- **Risk Stratification**: Multi-dimensional accident rate computation
- **Temporal Analysis**: Time-based pattern identification
- **Geographic Analysis**: State-level risk comparison
- **Weather Impact**: Weather condition correlation analysis

## Data Schema

Key columns analyzed:
- `ID`: Unique accident identifier
- `Start_Time`: Accident start timestamp  
- `State`: US state where accident occurred
- `Severity`: Accident severity level (1-4)
- `Weather_Condition`: Weather conditions during accident
- Additional contextual variables (temperature, visibility, etc.)

## Results & Insights

The analysis provides insights into:
- **Temporal Patterns**: Peak accident times and seasonal trends
- **Geographic Risk**: State-level accident distributions  
- **Severity Trends**: Changes in accident severity over time
- **Weather Impact**: Most common weather conditions by state
- **Risk Factors**: Key variables associated with accident occurrence

## Development Workflow

This project follows GitFlow methodology