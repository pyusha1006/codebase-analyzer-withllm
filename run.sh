#!/bin/bash
# Quick run script for Codebase Analyzer

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from env-example.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the analyzer
echo "🔍 Starting Codebase Analysis..."
echo ""
python main.py

echo ""
echo "✅ Analysis complete! Check output/analysis_results.json"

