#!/usr/bin/env python3
"""Test the exact usage pattern from the assignment."""

print("🎯 Testing assignment-specified usage pattern...")

# Exact usage from assignment
from accidents import RiskAnalyzer

analyzer = RiskAnalyzer(data_path='data/US_Accidents_March23.csv')
results = analyzer.compute_risk(levels=['State', 'Severity'])

print(f"✅ compute_risk() returned {len(results):,} records")
print(f"✅ Columns: {list(results.columns)}")
print("\n📊 Sample results:")
print(results.head())

# Clean up
analyzer.close()

print("\n🎉 Assignment usage pattern works perfectly!")
