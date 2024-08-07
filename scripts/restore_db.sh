#!/bin/bash

# check for argument
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <path_to_main.db>"
  exit 1
fi

FILE_PATH=$1

# check if file exists
if [ ! -f "$FILE_PATH" ]; then
  echo "File not found: $FILE_PATH"
  exit 1
fi

export CONTAINER_NAME=simple-tgbot-webapp-template-container
export BOT_FOLDER_NAME=simple-tgbot-webapp-template

docker cp "$FILE_PATH" ${CONTAINER_NAME}:/usr/src/app/${BOT_FOLDER_NAME}/data/main.db

if [ $? -eq 0 ]; then
  echo "File successfully copied to container."
else
  echo "Failed to copy file to container."
  exit 1
fi