#!/bin/bash

DOCKERIGNORE_FILE=".dockerignore"

# Initial content
echo ".idea
.vscode
.venv

frontend" > $DOCKERIGNORE_FILE

# Check if frontend directory exists
if [ -d "frontend" ]; then
    # Loop through each subdirectory in frontend
    for dir in frontend/*/; do
        # Remove trailing slash and get just the directory name
        dir_name=$(basename "$dir")
        # Add the exception for this directory's dist folder
        echo "!frontend/$dir_name/dist" >> $DOCKERIGNORE_FILE
    done
else
    echo "Warning: 'frontend' directory not found. No subdirectory exceptions added."
fi

echo ".dockerignore file has been generated."