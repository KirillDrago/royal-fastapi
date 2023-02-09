import sqlite3

from fastapi import FastAPI, Depends, HTTPException, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from telethon import TelegramClient, functions
from telethon.errors import ChatAdminRequiredError
from sqlalchemy.orm import Session
from models import SessionLocal, Token

app = FastAPI()
templates = Jinja2Templates(directory="templates")

conn = sqlite3.connect("tokens_db")
cursor = conn.cursor()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/start")
async def start(request: Request):
    data = await request.form()
    token = data["token"]
    cursor.execute("SELECT token FROM tokens WHERE token=?", (token,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(status_code=400, detail="Not authorized, contact please to administrator for your key.")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    data = await request.form()
    api_id = data["api_id"]
    api_hash = data["api_hash"]
    phone = data["phone"]

    global client
    client = TelegramClient(phone, int(api_id), api_hash)
    await client.connect()

    await client.send_code_request(phone)
    return templates.TemplateResponse("code.html", {"request": request})


@app.post("/code")
async def code(request: Request):
    data = await request.form()
    phone_code = data["phone_code"]
    phone = data["phone"]
    phone_code = data["phone_code"]
    global client
    client = await client.start(phone=str(phone), code_callback=lambda: phone_code)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/token")
async def token_validation(request: Request, db: Session = Depends(get_db)):
    data_token = await request.form()
    admin_token = data_token["admin-token"]
    token = data_token["store-token"]
    if admin_token == "xA480*u44b3q":
        db_token = Token(token=token)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return {"message": "Token stored"}
    return {"message: Admin token is invalid"}


@app.get("/store-token")
async def store_token(request: Request):
    return templates.TemplateResponse("store_token.html", {"request": request})


@app.get("/dialogs/{query}")
async def search_dialogs(request: Request, query: str):
    # Call the search_dialogs method to search for dialogs matching the query
    dialogs = await client(functions.contacts.SearchRequest(q=query, limit=100))
    chats = []
    chats.extend(dialogs.chats)

    # Extract the name and username of each dialog, and return the results as a list
    data = [{"num": chats.index(chat), "name": chat.title, "id": chat.id} for chat in chats]
    return templates.TemplateResponse("dialogs.html", {"request": request, "data": data})


@app.get("/dialogs/{query}/{chat_id}")
async def get_participants(request: Request, query: str, chat_id: int):
    async with client:
        # Connect to the Telegram servers and perform any required authorization
        dialogs = await client(functions.contacts.SearchRequest(q=query, limit=100))
        chats = []
        chats.extend(dialogs.chats)
        target_group = chats[int(chat_id)]

        # Call the get_participants method to get the participants in the chat
        try:
            participants = await client.get_participants(target_group)
        except ChatAdminRequiredError:
            data = [{"name": "You have no access to participants list"}]
        except ValueError:
            print("Wait please...")
        except RuntimeError:
            print("Wait please...")
        else:
            # Extract the name and username of each participant, and return the results as a list
            data = [{"num": participants.index(participant), "name": participant.first_name, "username": participant.username} for participant in
                    participants]
        return templates.TemplateResponse("members.html", {"request": request, "data": data})
