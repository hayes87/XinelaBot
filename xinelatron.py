# https://docs.google.com/spreadsheets/d/1NRhDtTA6CVb6JHFUoSUVtEg3H12o-MUE7c4n3dre9xw/edit#gid=0
from typing import Any
import utils.env as env
import discord
from discord.ext import commands
from utils.content import Content


class XinelaTron(commands.Bot):
    def __init__(self, **options: Any):
        super().__init__(command_prefix='!', intents=discord.Intents.all(), **options)

        self.content = Content()
        self.register_commands()
        self.run(env.BOT_TOKEN)

    def register_commands(self):
        @self.event
        async def on_ready():
            print(f'{self.user} has connected to Discord!')
            await self.load_extension("cogs.poll")

            self.tree.copy_global_to(guild=env.GUILDS_ID_OBJ)
            await self.tree.sync(guild=env.GUILDS_ID_OBJ)
