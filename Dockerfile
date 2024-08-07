FROM python:3.11-slim

ARG DOCKER_BOT_FOLDER_NAME
ENV BOT_FOLDER_NAME=${DOCKER_BOT_FOLDER_NAME}

WORKDIR /usr/src/app/${BOT_FOLDER_NAME}

COPY requirements.txt /usr/src/app/${BOT_FOLDER_NAME}/
RUN pip install -r requirements.txt

COPY . /usr/src/app/${BOT_FOLDER_NAME}/