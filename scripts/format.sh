#!/bin/bash

# Code formatting script
# This script runs black and isort to format all Python files

echo "🔧 Formatting Python code..."

echo "Running isort..."
uv run isort .

echo "Running black..."
uv run black .

echo "✅ Code formatting complete!"