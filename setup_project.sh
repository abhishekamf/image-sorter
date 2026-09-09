#!/bin/bash
echo "Setting up Duplicate Photo Cleaner project..."

# Create directory structure
mkdir -p src/{core,database,gui}
mkdir -p assets
mkdir -p build_scripts

# Create __init__.py files
touch src/__init__.py
touch src/core/__init__.py
touch src/database/__init__.py
touch src/gui/__init__.py

echo "✓ Project structure created"
