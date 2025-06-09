"""
Example usage of the US Accidents Analysis package.

This script demonstrates how to use the package for various types of analysis.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from accidents import RiskAnalyzer, AccidentVisualizer


def main():
    """Main example function demonstrating package usage."""
    
    # Data file path (adjust as needed)
    data_path = "data/US_Accidents.csv"
    
    if not Path(data_path).exists():
        print(f"❌ Data file not found: {data_path}")
        print("Please run download_data.py first or adjust the path")
        return
    
    print("🚀 US Accidents Analysis Package - Example Usage")
    print("=" * 60)
    
    # Example 1: Basic Risk Analysis
    print("\n📊 Example 1: Basic Risk Analysis")
    print("-" * 40)
    
    with RiskAnalyzer(data_path) as analyzer:
        # Compute risk metrics by State and Severity
        risk_metrics = analyzer.compute_risk(levels=['State', 'Severity'])
        print(f"✅ Computed {len(risk_metrics):,} risk metric records")
        print("Sample data:")
        print(risk_metrics.head())
        
        # Generate summary report
        summary = analyzer.generate_summary_report()
        print(f"\n📈 Dataset contains {summary['total_accidents']:,} total accidents")
        print(f"📅 Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
    
    # Example 2: Temporal Pattern Analysis
    print("\n⏰ Example 2: Temporal Pattern Analysis")
    print("-" * 40)
    
    with RiskAnalyzer(data_path) as analyzer:
        temporal_patterns = analyzer.compute_temporal_patterns()
        
        print("Available temporal patterns:")
        for pattern_type, data in temporal_patterns.items():
            print(f"  • {pattern_type}: {len(data)} records")
        
        # Show peak hours
        hourly_data = temporal_patterns['hourly']
        peak_hour = hourly_data.loc[hourly_data['accident_count'].idxmax()]
        print(f"🕐 Peak accident hour: {peak_hour['hour']:.0f}:00 ({peak_hour['accident_count']:,} accidents)")
    
    # Example 3: Weather Risk Analysis
    print("\n🌤️  Example 3: Weather Risk Analysis")
    print("-" * 40)
    
    with RiskAnalyzer(data_path) as analyzer:
        weather_risk = analyzer.compute_weather_risk()
        
        # Top weather conditions overall
        top_weather = weather_risk.groupby('Weather_Condition')['accident_count'].sum().nlargest(5)
        print("Top 5 weather conditions by accident count:")
        for weather, count in top_weather.items():
            print(f"  • {weather}: {count:,} accidents")
    
    # Example 4: State-Level Risk Analysis
    print("\n🗺️  Example 4: State-Level Risk Analysis")
    print("-" * 40)
    
    with RiskAnalyzer(data_path) as analyzer:
        state_risk = analyzer.compute_state_risk_rates()
        
        # Top 5 states by total accidents
        top_states = state_risk.groupby('State')['total_accidents'].sum().nlargest(5)
        print("Top 5 states by total accidents:")
        for state, count in top_states.items():
            print(f"  • {state}: {count:,} accidents")
        
        # States with highest severe accident rates
        latest_year = state_risk['year'].max()
        latest_data = state_risk[state_risk['year'] == latest_year]
        high_severity_states = latest_data.nlargest(5, 'severe_accident_rate')
        
        print(f"\nTop 5 states by severe accident rate ({latest_year:.0f}):")
        for _, row in high_severity_states.iterrows():
            print(f"  • {row['State']}: {row['severe_accident_rate']:.1f}% severe accidents")
    
    # Example 5: Creating Visualizations
    print("\n📊 Example 5: Creating Visualizations")
    print("-" * 40)
    
    # Initialize visualizer
    visualizer = AccidentVisualizer()
    
    with RiskAnalyzer(data_path) as analyzer:
        # Get data for visualization
        state_totals = analyzer.compute_state_risk_rates()
        state_summary = state_totals.groupby('State')['total_accidents'].sum().reset_index()
        
        # Create geographic distribution plot
        print("📈 Creating geographic distribution visualization...")
        fig1 = visualizer.plot_geographic_distribution(state_summary, top_n=10)
        
        # Save the plot
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        visualizer.save_figure(fig1, "example_geographic.png", str(output_dir))
        
        # Create temporal patterns plot
        print("📈 Creating temporal patterns visualization...")
        temporal_data = analyzer.compute_temporal_patterns()
        fig2 = visualizer.plot_time_patterns(temporal_data)
        visualizer.save_figure(fig2, "example_temporal.png", str(output_dir))
        
        print(f"✅ Visualizations saved to {output_dir}/")
    
    # Example 6: Interactive Visualization
    print("\n🎯 Example 6: Interactive Visualization")
    print("-" * 40)
    
    with RiskAnalyzer(data_path) as analyzer:
        # Get annual state data
        annual_data = analyzer.compute_state_risk_rates()
        
        # Create interactive plot
        interactive_fig = visualizer.create_interactive_state_trends(annual_data, top_n=5)
        
        # Save as HTML
        interactive_fig.write_html(output_dir / "interactive_trends.html")
        print(f"✅ Interactive visualization saved to {output_dir}/interactive_trends.html")
    
    print("\n🎉 All examples completed successfully!")
    print(f"📁 Check the {output_dir}/ directory for generated files")


def advanced_example():
    """Advanced usage example with custom analysis."""
    
    print("\n🔬 Advanced Example: Custom Multi-Dimensional Analysis")
    print("=" * 60)
    
    data_path = "data/US_Accidents.csv"
    
    with RiskAnalyzer(data_path) as analyzer:
        # Custom risk analysis with multiple dimensions
        print("🎯 Computing multi-dimensional risk metrics...")
        
        # Risk by State, Severity, and Weather (without time dimensions)
        risk_results = analyzer.compute_risk(
            levels=['State', 'Severity', 'Weather_Condition'],
            include_time=False
        )
        
        print(f"✅ Computed {len(risk_results):,} multi-dimensional risk records")
        
        # Find the most dangerous combinations
        top_combinations = risk_results.nlargest(10, 'accident_count')
        
        print("\n🚨 Most dangerous State-Severity-Weather combinations:")
        for _, row in top_combinations.iterrows():
            print(f"  • {row['State']}, Severity {row['Severity']}, {row['Weather_Condition']}: "
                  f"{row['accident_count']:,} accidents")
        
        # Analyze severity patterns by weather
        severity_weather = risk_results.groupby(['Severity', 'Weather_Condition'])['accident_count'].sum().reset_index()
        
        print("\n📊 Creating advanced weather-severity visualization...")
        # Custom analysis could go here
        
        print("✅ Advanced analysis completed!")


if __name__ == "__main__":
    # Run basic examples
    main()
    
    # Uncomment to run advanced example
    # advanced_example()