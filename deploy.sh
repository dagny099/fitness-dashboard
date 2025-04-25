#!/bin/bash

cd /home/ubuntu/fitness-dashboard || exit
git pull origin main
source .venv-dash/bin/activate
pip install -r requirements.txt
sudo systemctl restart sql-dashboard.service
