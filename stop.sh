#!/bin/bash

docker rm $(docker stop fromsub)
docker image rm fromsub
