"""
Setup script for the US Accidents Risk Analysis package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    requirements = (this_directory / "requirements.txt").read_text().splitlines()
    # Filter out comments and empty lines
    requirements = [req for req in requirements if req and not req.startswith('#')]

setup(
    name="us-accidents-risk",
    version="1.0.0",
    author="Bella Qian",
    author_email="qyzanemos@gmail.com",
    description="A comprehensive package for analyzing US traffic accident patterns and public health risks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/us-accidents-risk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "duckdb>=0.8.0",
        "jupyter>=1.0.0",
        "kaggle>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "us-accidents-download=scripts.download_data:main",
            "us-accidents-analyze=scripts.risk_analysis:main",
        ],
    },
    include_package_data=True,
    package_data={
        "accidents": ["*.py"],
    },
)