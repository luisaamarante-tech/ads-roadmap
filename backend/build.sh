#!/usr/bin/env bash
# Build script for Render deployment
# https://render.com/docs/deploy-flask

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating data directory for cache..."
mkdir -p data

echo "Build completed successfully!"
