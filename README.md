# CopyLeft AI API
This repository contains the back-end infrastructure for the CopyLeft AI Annotator located here: https://github.com/arthurwolf/annotator.

# Installation
## Using Docker and Docker-Compose
- build the images and start the containers with `docker-compose up -d`
- tear them down with `docker-compose down`
- stop them with `docker-compose stop`
- start them with `docker-compose start`
## Using Kubernetes
Coming Soon

# Accessing the Applications
## CLAIF API (FastAPI)
### Swagger Docs (Swagger UI)
- visit http://localhost:8082/docs
<img src="./screenshots/claif-api-swagger.png" style="max-width: 600px;" />
### Redoc Docs
- visit http://localhost:8082/redoc
<img src="./screenshots/claif-api-redoc.png" style="max-width: 600px;" />

## Adminer
A lightweight browser-based database administration utility.
- visit http://localhost:8083
<img src="./screenshots/adminer-1.png" style="max-width: 600px;" />
<img src="./screenshots/adminer-2.png" style="max-width: 600px;" />
