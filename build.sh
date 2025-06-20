#!/bin/bash

# Upgrade pip first (optional but recommended)
pip install --upgrade pip

# Install numpy first (needed by basicsr and others)
pip install numpy

# Install opencv-python BEFORE basicsr to avoid cv2 import error
pip install opencv-python

# Install torch and torchvision together to ensure compatibility
pip install torch==2.7.1 torchvision==0.15.2

# Now install the rest of your requirements, including basicsr
pip install -r requirements.txt
