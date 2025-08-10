#!/bin/bash

# Linting script
# This script runs flake8 to check for code quality issues

echo "🔍 Running code quality checks..."

echo "Running flake8..."
if uv run flake8 backend/ main.py; then
    echo "✅ No linting issues found!"
else
    echo "❌ Linting issues found. Please fix them before committing."
    exit 1
fi