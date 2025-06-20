#!/bin/bash

# Upgrade pip, setuptools, and wheel first (important for build system compatibility)
pip install --upgrade pip setuptools wheel

# Install numpy first (needed by basicsr and others)
pip install numpy

# Install opencv-python BEFORE basicsr to avoid cv2 import error
pip install opencv-python

# Install torch and torchvision together with compatible versions.
# NOTE: torch 2.7.1 and torchvision 0.15.2 are not available for Python 3.13.
# If using Python 3.13, consider these versions or adjust Python version to 3.10/3.11:
# For Python 3.13 (adjust as needed):
# pip install torch==2.0.1 torchvision==0.21.0
#
# For Python 3.10/3.11 (recommended for best compatibility):
pip install torch==2.0.1 torchvision==0.21.0

# TEMP PATCH: Prevent basicsr from importing torch during setup
export PATCH_BASICSR_DIR=$(mktemp -d)
pip download basicsr==1.3.4 -d "$PATCH_BASICSR_DIR" --no-deps
cd "$PATCH_BASICSR_DIR"
tar -xf basicsr-1.3.4.0.tar.gz
cd basicsr-1.3.4.0

# Comment out the torch import line in setup.py
sed -i 's/^import torch/# import torch/' setup.py

# Install patched basicsr manually
pip install .
cd ../..


# Now install the rest of your requirements, including basicsr
pip install -r requirements.txt
