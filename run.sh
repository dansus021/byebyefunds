#!/bin/bash
cd \"$(dirname \"$0\")\"
apt-get update && apt-get install -y python3-pip
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 liqfinal.py
