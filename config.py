# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os
from dotenv import load_dotenv

load_dotenv()

# VPS --- FILL COOKIES 🍪 in """ ... """ 

INST_COOKIES = """
# wtite up here insta cookies
"""

YTUB_COOKIES = """
# write here yt cookies
"""

API_ID = os.getenv("API_ID", "25637343")
API_HASH = os.getenv("API_HASH", "70fb79a89ec2d30cab05704e817e5be6")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7799682099:AAGuTUXqB67HVNf1XJWoTGFCYPywYaSk04s")
MONGO_URI = os.getenv("MONGO_DB", "mongodb+srv://ellie535091:A8sx0Q3dVNPPku18@cluster0.ry133.mongodb.net/?retryWrites=true&w=majority")
OWNER_ID = list(map(int, os.getenv("OWNER_ID", "5390137933").split())) # list seperated via space
DB_NAME = os.getenv("DB_NAME", "Sunilvs2024")
STRING = os.getenv("STRING", None) # optional
LOG_GROUP = int(os.getenv("LOG_GROUP", "-1002039915658")) # optional with -100
FORCE_SUB = int(os.getenv("FORCE_SUB", "-1002386527380")) # optional with -100
YT_COOKIES = os.getenv("YT_COOKIES", YTUB_COOKIES)
INSTA_COOKIES = os.getenv("INSTA_COOKIES", INST_COOKIES)
