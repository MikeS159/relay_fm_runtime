#!/bin/bash
git pull
rm README.md
python3 relay.py > README.md
git add .
git commit -m "Updates show run times"
git push
