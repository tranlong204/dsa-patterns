#!/bin/bash

echo "Setting up DSA Patterns Backend..."
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please update .env with your Supabase credentials:"
    echo "   SUPABASE_URL=your_supabase_url"
    echo "   SUPABASE_KEY=your_supabase_key"
    echo ""
fi

# Print setup instructions
echo "📋 Next steps:"
echo "1. Update .env with your Supabase credentials"
echo "2. Run the SQL in backend/supabase_migration.sql in your Supabase SQL Editor"
echo "3. Run: python import_data.py (to import problems from data.js)"
echo "4. Start the server: uvicorn app.main:app --reload"
echo ""
echo "Done! 🎉"

