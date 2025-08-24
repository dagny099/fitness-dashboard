#!/bin/bash
# Deploy the latest Fitness Dashboard build

echo "🚀 Starting Fitness Dashboard deployment..."

cd /home/ubuntu/fitness-dashboard || exit 1

echo "📥 Pulling latest changes..."
git pull origin main

echo "🔄 Activating virtual environment..."
source .venv-dash/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Restarting service..."
sudo systemctl restart sql-dashboard.service

echo "✅ Deployment completed successfully!"
echo "🌐 Dashboard should be available at your configured URL"
