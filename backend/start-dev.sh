#!/bin/bash

# JEVO Incidents Backend - Development Start Script

echo "🚀 Starting JEVO Incidents Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your configuration."
fi

# Start uvicorn server with hot reload
echo "🔄 Starting server with hot reload..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
