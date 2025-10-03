#!/bin/bash

# Quick setup script for Raspberry Pi
# Run this after cloning the repository

echo "================================"
echo "ELEC290 Setup Script"
echo "================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "This script should be run on the Raspberry Pi, not your Mac"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-opencv libatlas-base-dev

echo ""
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

echo ""
echo "📥 Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Wire your HC-SR04 sensor (see WIRING.md)"
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the application:"
echo "   python app.py"
echo "4. Access from your Mac:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "================================"
