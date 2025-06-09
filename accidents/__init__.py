"""
US Accidents Risk Analysis Package

A comprehensive package for analyzing traffic accident patterns and public health risks
using the US Accidents dataset.

Example usage:
    from accidents import RiskAnalyzer
    
    analyzer = RiskAnalyzer(data_path='data/US_Accidents.csv')
    results = analyzer.compute_risk(levels=['State', 'Severity'])
"""

__version__ = "1.0.0"
__author__ = "Bella Qian"
__email__ = "qyzanemos@gmail.com"

from .analyzer import RiskAnalyzer
from .data_loader import DataLoader
from .visualizations import AccidentVisualizer

__all__ = [
    'RiskAnalyzer',
    'DataLoader', 
    'AccidentVisualizer'
]