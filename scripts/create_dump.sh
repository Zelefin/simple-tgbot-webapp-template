#!/bin/bash

export CONTAINER_NAME=simple-tgbot-webapp-template-container
export BOT_FOLDER_NAME=simple-tgbot-webapp-template
mkdir -p ./dump
docker cp ${CONTAINER_NAME}:/usr/src/app/${BOT_FOLDER_NAME}/data/main.db ./dump/main.db

if [ $? -eq 0 ]; then
  echo "Dump successfully created."
else
  echo "Failed to create dump."
  exit 1
fi