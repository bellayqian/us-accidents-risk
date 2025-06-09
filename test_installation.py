from accidents import RiskAnalyzer

print("✅ Package imported successfully!")

# Test with your actual data file
try:
    analyzer = RiskAnalyzer('data/US_Accidents_March23.csv')
    print("✅ RiskAnalyzer initialized successfully!")
    analyzer.close()
except Exception as e:
    print(f"⚠️  Note: {e}")

print("🎉 Package installation test completed!")
