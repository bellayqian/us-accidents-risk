"""
Command-line interface for the US Accidents package.
"""

import argparse
import sys
from pathlib import Path
from .analyzer import RiskAnalyzer
from .visualizations import AccidentVisualizer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="US Accidents Risk Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  accidents-analyze --data data/US_Accidents.csv --analysis risk
  accidents-analyze --data data/US_Accidents.csv --analysis temporal --output results/
  accidents-analyze --data data/US_Accidents.csv --summary
        """
    )
    
    parser.add_argument(
        "--data", "-d",
        required=True,
        help="Path to US Accidents CSV file"
    )
    
    parser.add_argument(
        "--analysis", "-a",
        choices=["risk", "temporal", "weather", "severity", "all"],
        default="all",
        help="Type of analysis to perform"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="outputs/",
        help="Output directory for results and visualizations"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate summary report only"
    )
    
    parser.add_argument(
        "--levels",
        nargs="+",
        default=["State", "Severity"],
        help="Grouping levels for risk analysis"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualizations"
    )
    
    args = parser.parse_args()
    
    # Validate data file
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ Error: Data file not found: {args.data}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 Starting US Accidents Analysis...")
    print(f"📁 Data file: {data_path}")
    print(f"💾 Output directory: {output_dir}")
    
    try:
        # Initialize analyzer
        with RiskAnalyzer(data_path) as analyzer:
            
            if args.summary:
                print("\n📊 Generating summary report...")
                summary = analyzer.generate_summary_report()
                
                print(f"\n📈 Dataset Summary:")
                print(f"   Total accidents: {summary['total_accidents']:,}")
                print(f"   Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
                print(f"   States covered: {summary['states_covered']}")
                
                # Save summary to file
                import json
                with open(output_dir / "summary_report.json", "w") as f:
                    # Convert non-serializable objects to strings
                    serializable_summary = {
                        'total_accidents': summary['total_accidents'],
                        'date_range': [str(summary['date_range'][0]), str(summary['date_range'][1])],
                        'states_covered': summary['states_covered'],
                        'top_states': summary['top_states'].to_dict('records'),
                        'severity_distribution': summary['severity_distribution'].to_dict('records')
                    }
                    json.dump(serializable_summary, f, indent=2)
                
                print(f"✅ Summary saved to {output_dir / 'summary_report.json'}")
                return
            
            # Perform requested analysis
            if args.analysis in ["risk", "all"]:
                print("\n🎯 Computing risk metrics...")
                risk_results = analyzer.compute_risk(levels=args.levels)
                risk_results.to_csv(output_dir / "risk_metrics.csv", index=False)
                print(f"✅ Risk metrics saved to {output_dir / 'risk_metrics.csv'}")
            
            if args.analysis in ["temporal", "all"]:
                print("\n⏰ Analyzing temporal patterns...")
                temporal_results = analyzer.compute_temporal_patterns()
                
                for pattern_type, data in temporal_results.items():
                    filename = f"temporal_{pattern_type}.csv"
                    data.to_csv(output_dir / filename, index=False)
                    print(f"✅ {pattern_type.title()} patterns saved to {output_dir / filename}")
            
            if args.analysis in ["weather", "all"]:
                print("\n🌤️  Analyzing weather patterns...")
                weather_results = analyzer.compute_weather_risk()
                weather_results.to_csv(output_dir / "weather_analysis.csv", index=False)
                print(f"✅ Weather analysis saved to {output_dir / 'weather_analysis.csv'}")
            
            # Generate visualizations if requested
            if args.visualize:
                print("\n📊 Generating visualizations...")
                visualizer = AccidentVisualizer()
                
                if args.analysis in ["risk", "all"]:
                    # Get state totals for visualization
                    state_totals = analyzer.compute_state_risk_rates()
                    state_summary = state_totals.groupby('State')['total_accidents'].sum().reset_index()
                    
                    fig = visualizer.plot_geographic_distribution(state_summary)
                    visualizer.save_figure(fig, "geographic_distribution.png", str(output_dir))
                    plt.close(fig)
                
                if args.analysis in ["temporal", "all"]:
                    temporal_data = analyzer.compute_temporal_patterns()
                    fig = visualizer.plot_time_patterns(temporal_data)
                    visualizer.save_figure(fig, "time_patterns.png", str(output_dir))
                    plt.close(fig)
                
                print("✅ Visualizations saved to output directory")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)
    
    print("\n🎉 Analysis completed successfully!")
    print(f"📁 Results available in: {output_dir}")


if __name__ == "__main__":
    main()