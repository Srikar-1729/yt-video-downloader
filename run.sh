#!/bin/bash

echo "Starting YouTube Video Downloader..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting Flask server..."
python backend/app.py
