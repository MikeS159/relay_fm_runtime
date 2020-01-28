#!/bin/bash
git pull
python3 relay.py
git add .
git commit -m "Updates show run times"
git push
