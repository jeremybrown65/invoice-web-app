#!/bin/bash
cd "$(dirname "$0")"

# Add local bin directory to PATH so app uses the bundled binaries
export PATH="$PWD/bin:$PATH"

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run app.py
