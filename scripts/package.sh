#!/bin/bash

# Define variables
STAGING_DIR="build"
REQUIREMENTS_FILE="requirements.txt"
ZIP_FILE="udf_package.zip"
PYTHON_VERSION="python3"  # Adjust this if needed (e.g., python3.8)

# Clean previous builds
rm -rf $STAGING_DIR
rm -f $ZIP_FILE

# Create build directory
mkdir -p $STAGING_DIR

# Set up virtual environment
$PYTHON_VERSION -m venv $STAGING_DIR/venv
source $STAGING_DIR/venv/bin/activate

# Install dependencies in a specific folder
pip install -r $REQUIREMENTS_FILE -t $STAGING_DIR/libs

# Copy the code files into the staging directory
cp utils.py UDFs.py $STAGING_DIR/

# Zip everything (code and dependencies)
cd $STAGING_DIR
zip -r ../$ZIP_FILE ./*

# Deactivate virtual environment
deactivate

# Cleanup
cd ..
rm -rf $STAGING_DIR

echo "Packaged and zipped successfully into $ZIP_FILE"
