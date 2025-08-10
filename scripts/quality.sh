#!/bin/bash

# Complete quality check script
# This script runs formatting and linting

echo "🚀 Running complete code quality checks..."

# Run formatting first
echo "Step 1: Formatting code..."
./scripts/format.sh

# Then run linting
echo "Step 2: Checking code quality..."
./scripts/lint.sh

echo "✅ All quality checks complete!"