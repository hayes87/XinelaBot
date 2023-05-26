import discord
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID_INT = int(os.getenv("GUILD_ID"))
GUILDS_ID_OBJ = discord.Object(id=os.getenv("GUILD_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))
ELEVENLABS_API = os.getenv("ELEVENLABS_API")
CREDENTIAL_JSON = os.getenv("CREDENTIAL_JSON")
