#!/bin/bash

# Install numpy first
pip install numpy

# Install torch (already done, keep it if needed)
pip install torch==2.7.1

# Then install rest, including basicsr
pip install -r requirements.txt
