import re
import os
from os import environ
from Script import script

# Pattern to validate admin/user IDs
id_pattern = re.compile(r'^.\d+$')

# Helper function to parse boolean-like environment values
def is_enabled(value, default):
    if isinstance(value, str):
        value = value.lower()
        if value in ["true", "yes", "1", "enable", "y"]:
            return True
        elif value in ["false", "no", "0", "disable", "n"]:
            return False
    return default

# Bot Information
API_ID = int(environ.get("API_ID", "25230605"))
API_HASH = environ.get("API_HASH", "b7d6c13e37d52cbbea25742f1c8b40cd")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

PICS = environ.get('PICS', 'https://graph.org/file/ce1723991756e48c35aa1.jpg').split()
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '6392951002').split()]
BOT_USERNAME = environ.get("BOT_USERNAME", "Mms_hub18_bot")  # without @
PORT = environ.get("PORT", "8080")

# Clone Info
CLONE_MODE = is_enabled(environ.get('CLONE_MODE', "False"), False)
CLONE_DB_URI = environ.get("CLONE_DB_URI", "")
CDB_NAME = environ.get("CDB_NAME", "clonemmshub18")

# Database Information
DB_URI = environ.get("DB_URI", "mongodb+srv://facknet1999:GjMN6ZY5R3AbPx56@cluster0.6a3fnf0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = environ.get("DB_NAME", "mmshub18")

# Auto Delete Information
AUTO_DELETE_MODE = is_enabled(environ.get('AUTO_DELETE_MODE', "True"), True)
AUTO_DELETE = int(environ.get("AUTO_DELETE", "30"))  # in minutes
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "1800"))  # in seconds

# Channel Information
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "1002663679629"))

# File Caption
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# Public Access
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)

# Verification System
VERIFY_MODE = is_enabled(environ.get('VERIFY_MODE', "True"), True)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "bharatlinks.com")
SHORTLINK_API = environ.get("SHORTLINK_API", "229853ecbbbbd01d73da405efce80c3acb8654ca")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/alltutorial_mms/4")

# Website Integration
WEBSITE_URL_MODE = is_enabled(environ.get('WEBSITE_URL_MODE', "False"), False)
WEBSITE_URL = environ.get("WEBSITE_URL", "")

# Streaming
STREAM_MODE = is_enabled(environ.get('STREAM_MODE', "False"), False)
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))

# Heroku Environment Detection
ON_HEROKU = 'DYNO' in environ
URL = environ.get("URL", "")
