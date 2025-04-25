#!/bin/bash
# Deploy the latest Fitness Dashboard build

cd /home/ubuntu/fitness-dashboard || exit 1
git pull origin main
source .venv-dash/bin/activate
pip install -r requirements.txt
sudo systemctl restart sql-dashboard.service
