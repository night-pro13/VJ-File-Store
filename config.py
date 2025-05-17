import re
import os
import time
import asyncio
from datetime import datetime, timedelta
from os import environ
import requests
from pyrogram import Client, filters
from pymongo import MongoClient

def is_enabled(value, default):
    if isinstance(value, str):
        value = value.lower()
        if value in ["true", "yes", "1", "enable", "y"]:
            return True
        elif value in ["false", "no", "0", "disable", "n"]:
            return False
    return default

API_ID = int(environ.get("API_ID", "25230605"))
API_HASH = environ.get("API_HASH", "b7d6c13e37d52cbbea25742f1c8b40cd")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

ADMINS = list(map(int, environ.get("ADMINS", "6392951002").split()))

# MongoDB connection
DB_URI = "mongodb+srv://facknet1999:GjMN6ZY5R3AbPx56@cluster0.6a3fnf0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = environ.get("DB_NAME", "mmshub18")

# URL shortener config
SHORTLINK_URL = "bharatlinks.com"
SHORTLINK_API = "229853ecbbbbd01d73da405efce80c3acb8654ca"

# Auto delete time in seconds (30 minutes)
AUTO_DELETE_TIME = 30 * 60
# Shortlink validity (6 hours)
SHORTLINK_VALIDITY = 6 * 60 * 60

mongo_client = MongoClient(DB_URI)
db = mongo_client[DB_NAME]
files_collection = db.files
access_collection = db.accesses  # To track user access timestamps for files

app = Client("permanent_file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def is_admin(user_id):
    return user_id in ADMINS

def shorten_url(long_url: str) -> str:
    api_url = f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={long_url}"
    try:
        response = requests.get(api_url)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl", long_url)
        else:
            return long_url
    except Exception:
        return long_url

async def auto_delete_old_files():
    while True:
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=AUTO_DELETE_TIME)
        result = files_collection.delete_many({"stored_at": {"$lt": cutoff}})
        if result.deleted_count > 0:
            print(f"Auto deleted {result.deleted_count} old files.")
        await asyncio.sleep(300)  # check every 5 minutes

@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "Welcome to Permanent File Store Bot!\n"
        "Send me any file and I will store it permanently with a short URL.\n"
        "Use /help to see commands."
    )

@app.on_message(filters.private & filters.command("help"))
async def help_handler(client, message):
    await message.reply_text(
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/myfiles - List your stored files\n"
        "/get <file_id> - Access your stored file (passes shortlink verification)\n"
        "/delete <file_id> - Delete a stored file (admins only)\n"
    )

@app.on_message(filters.private & filters.command("myfiles"))
async def myfiles_handler(client, message):
    user_id = message.from_user.id
    files = files_collection.find({"user_id": user_id})

    if files.count() == 0:
        await message.reply_text("You have not stored any files yet.")
        return

    response = "Your stored files:\n"
    for f in files:
        response += f"- ID: {f['_id']}\n  Name: {f.get('file_name', 'Unknown')}\n\n"

    await message.reply_text(response)

@app.on_message(filters.private & filters.command("delete"))
async def delete_handler(client, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply_text("You are not authorized to delete files.")
        return

    args = message.text.split()
    if len(args) != 2:
        await message.reply_text("Usage: /delete <file_id>")
        return

    file_id = args[1]
    result = files_collection.delete_one({"_id": file_id})
    if result.deleted_count:
        await message.reply_text(f"File {file_id} deleted from the database.")
    else:
        await message.reply_text(f"File {file_id} not found.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def store_file_handler(client, message):
    user_id = message.from_user.id

    file_id = None
    file_name = None

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name
    elif message.photo:
        photo_sizes = message.photo
        file_id = photo_sizes[-1].file_id
        file_name = "photo.jpg"
    else:
        await message.reply_text("Unsupported file type.")
        return

    tg_url = f"https://t.me/{app.username}?start=files_{file_id}"
    short_url = shorten_url(tg_url)

    files_collection.insert_one({
        "_id": file_id,
        "user_id": user_id,
        "file_name": file_name,
        "tg_file_id": file_id,
        "short_url": short_url,
        "stored_at": datetime.utcnow()
    })

    await message.reply_text(f"Your file is saved permanently!\nAccess it here with:\n/get {file_id}\n\nYou will have to pass the shortlink verification before access.")

@app.on_message(filters.private & filters.command("get"))
async def get_file_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) != 2:
        await message.reply_text("Usage: /get <file_id>")
        return

    file_id = args[1]

    file_data = files_collection.find_one({"_id": file_id, "user_id": user_id})
    if not file_data:
        await message.reply_text("File not found or not owned by you.")
        return

    # Check access collection for this user and file
    access_record = access_collection.find_one({"user_id": user_id, "file_id": file_id})
    now = datetime.utcnow()

    if access_record:
        last_access = access_record.get("last_access")
        if last_access and (now - last_access).total_seconds() < SHORTLINK_VALIDITY:
            # Access allowed, send file link directly
            await message.reply_text(f"Here is your file link:\n{file_data['short_url']}")
            return
        else:
            # Access expired, delete old access record
            access_collection.delete_one({"_id": access_record["_id"]})

    # Access not granted or expired, send shortlink to re-bypass
    await message.reply_text(
        f"Please open this shortlink to verify access (valid for 6 hours):\n{file_data['short_url']}\n\n"
        f"Then send /get {file_id} again to get your file link."
    )

@app.on_message(filters.private & filters.command("verify"))
async def verify_handler(client, message):
    # Optional: if you want to implement a way user can "verify" manually after visiting the link
    pass

async def main():
    asyncio.create_task(auto_delete_old_files())
    await app.start()
    print("Bot started")
    await idle()
    await app.stop()

if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
