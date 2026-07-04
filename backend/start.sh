#!/bin/bash
set -e

echo "Starting NIARAD Backend on Render..."

# Create necessary directories
mkdir -p ./data ./generated_files ./uploads

# Run the application
echo "Starting Uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}