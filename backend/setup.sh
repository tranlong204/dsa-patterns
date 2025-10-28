#!/bin/bash

echo "Setting up DSA Patterns Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp env.example .env
    echo ""
    echo "⚠️  Please update .env with your Supabase credentials:"
    echo "   SUPABASE_URL=your_supabase_url"
    echo "   SUPABASE_KEY=your_supabase_key"
    echo ""
fi

# Print setup instructions
echo ""
echo "📋 Next steps:"
echo "1. Update .env with your Supabase credentials"
echo "2. Run the SQL in supabase_migration.sql in your Supabase SQL Editor"
echo "3. Run: python import_data.py (to import problems from data.js)"
echo "4. Activate venv and start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "Done! 🎉"

