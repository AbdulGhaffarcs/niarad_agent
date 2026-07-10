#!/bin/bash
set -e

echo "Starting NIARAD Backend..."

# Create necessary directories
mkdir -p "${NIARAD_DATA_DIR:-.}" "${NIARAD_GENERATED_FILES_DIR:-${NIARAD_DATA_DIR:-.}/generated_files}" "${NIARAD_UPLOADS_DIR:-${NIARAD_DATA_DIR:-.}/uploads}"

# Run the application
echo "Starting Uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
