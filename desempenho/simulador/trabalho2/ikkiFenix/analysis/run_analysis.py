#!/usr/bin/env python3
"""
Queueing System Analysis Runner
Executes the comprehensive analysis pipeline on simulation results.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the parent directory to path to import dataAnalysis
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dataAnalysis import ComprehensiveQueueAnalysis
except ImportError as e:
    print(f"Error importing analysis module: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive queueing system analysis')
    parser.add_argument('--input-dir', '-i', default='results', 
                       help='Input directory with CSV results')
    parser.add_argument('--output-dir', '-o', default='results/comprehensive_analysis',
                       help='Output directory for analysis results')
    parser.add_argument('--config', '-c', default='analysis_config.json',
                       help='Analysis configuration file')
    
    args = parser.parse_args()
    
    print("Queueing System Analysis Pipeline")
    print("=" * 50)
    
    # Verify input directory exists
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"Error: Input directory '{args.input_dir}' does not exist")
        sys.exit(1)
    
    # Create output directory if needed
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize and run analysis
        analyzer = ComprehensiveQueueAnalysis()
        
        # Override configuration if needed
        analyzer.config.data_directory = input_path
        analyzer.config.output_directory = output_path
        
        print(f"Input directory: {input_path}")
        print(f"Output directory: {output_path}")
        print("Starting analysis...")
        
        success = analyzer.run_comprehensive_analysis()
        
        if success:
            print("Analysis completed successfully!")
            print(f"Results saved to: {output_path}")
        else:
            print("Analysis failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Analysis error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()