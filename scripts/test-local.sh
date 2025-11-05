#!/bin/bash
# Local testing script - run before pushing to avoid CI failures
# This replicates the GitHub Actions CI checks locally

set -e  # Exit on first error

echo "🧪 Running local tests..."
echo ""

# Change to project root
cd "$(dirname "$0")/.."

echo "📦 Installing dependencies..."
pip install -e ".[dev]" > /dev/null 2>&1

echo ""
echo "🔍 1/4 Running ruff lint..."
ruff check gtext/

echo ""
echo "🎨 2/4 Checking code formatting with black..."
black --check gtext/

echo ""
echo "🧪 3/4 Running pytest with coverage..."
pytest --cov=gtext --cov-report=term-missing

echo ""
echo "📝 4/4 Running mypy (optional, errors won't fail)..."
mypy gtext/ || echo "⚠️  Mypy found issues (non-blocking)"

echo ""
echo "✅ All local tests passed! Safe to push."
echo ""
echo "⚠️  Note: Windows-specific tests cannot be run locally on macOS"
