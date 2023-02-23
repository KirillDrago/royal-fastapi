# royal-fastapi
This repository contains a FastAPI application for searching and retrieving members of Telegram groups using the Telethon library.

## Installation
```shell
git clone https://github.com/<username>/<repository>.git
pip install -r requirements.txt
uvicorn main:app --reload
```

## Run with docker
Docker should be installed
```shell
docker build -t <image-name> . 
docker run -p 8000:8000 <image-name>
```
## Usage
- At home page you need to enter admin key (xA480*u44b3q)
- To get app_id and app_hash:
  - Go to and log in to https://my.telegram.org
  - Go to https://my.telegram.org/auth?to=apps
  - Form placeholder
  - Get app_id and app_hash
  - Paste them below
- /search - Enter keyword for seearch list of chats
- /store-token - endpoint for create new token for other users
