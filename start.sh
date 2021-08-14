#!/bin/bash

docker build --build-arg TELEGRAMBOT_TOKEN=$TELEGRAMBOT_TOKEN -t fromsub .
docker run -d -p 80:80 -it --name fromsub fromsub
