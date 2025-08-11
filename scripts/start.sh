#!/bin/bash

# Echo Chamber Explorer - Startup Script

echo "Starting Echo Chamber Explorer..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data if needed
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Initialize database
echo "Initializing database..."
python -c "from app import init_db; init_db()"

# Start the application
echo "Starting Flask application..."
echo "Visit http://localhost:5000 to access Echo Chamber Explorer"
echo "Press Ctrl+C to stop the server"

export FLASK_ENV=development
python app.py
