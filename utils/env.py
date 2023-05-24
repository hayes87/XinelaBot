import discord
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID_INT = int(os.getenv("GUILD_ID"))
GUILD_ID_DEBUG_INT = int(os.getenv("GUILD_ID_DEBUG"))
GUILDS_ID_OBJ = discord.Object(id=os.getenv("GUILD_ID"))
GUILDS_ID_DEBUG_OBJ = discord.Object(id=os.getenv("GUILD_ID_DEBUG"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHANNEL_ID_DEBUG = int(os.getenv("CHANNEL_ID_DEBUG"))
ROLE_ID = int(os.getenv("ROLE_ID"))
ROLE_ID_DEBUG = int(os.getenv("ROLE_ID_DEBUG"))
