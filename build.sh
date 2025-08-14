#!/bin/bash
# Force binary distribution installation
pip install --upgrade pip setuptools wheel
pip install --prefer-binary -r requirements.txt
