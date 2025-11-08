#!/bin/bash

echo "==============================================="
echo "CAPTCHA Dental AI - Quick Setup & Fix"
echo "==============================================="

# Navigate to backend
cd backend

echo ""
echo "Step 1: Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 2: Testing server imports..."
python -c "from main import app; print('✓ Server imports successful')"

if [ $? -eq 0 ]; then
    echo "✓ All imports working"
else
    echo "✗ Server imports failed"
    exit 1
fi

echo ""
echo "Step 3: Running integration tests..."
python scripts/test_integration.py

echo ""
echo "==============================================="
echo "✅ Setup Complete!"
echo "==============================================="
echo ""
echo "To start the server:"
echo "  cd backend"
echo "  uvicorn main:app --reload"
echo ""
echo "Then visit: http://localhost:8000/docs"
echo "==============================================="
