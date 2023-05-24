# https://docs.google.com/spreadsheets/d/1NRhDtTA6CVb6JHFUoSUVtEg3H12o-MUE7c4n3dre9xw/edit#gid=0
from typing import Any
import utils.env as env
import discord
from discord.ext import commands
from utils.content import Content

class XinelaTron(commands.Bot):
    def __init__(self, debug=False, **options: Any):
        super().__init__(command_prefix='!', intents=discord.Intents.all(), **options)
        self.CHANNEL_ID = env.CHANNEL_ID if not debug else env.CHANNEL_ID_DEBUG
        self.role_id = env.ROLE_ID if not debug else env.ROLE_ID_DEBUG
        self.guild_id = env.CHANNEL_ID if not debug else env.CHANNEL_ID_DEBUG

        self.content = Content()
        self.register_commands(debug)
        self.run(env.BOT_TOKEN)

    def register_commands(self, debug):
        @self.event
        async def on_ready():
            print(f'{self.user} has connected to Discord!')
            await self.load_extension("cogs.poll")

            self.tree.copy_global_to(guild=env.GUILDS_ID_OBJ if not debug else env.GUILDS_ID_DEBUG_OBJ)
            await self.tree.sync(guild=env.GUILDS_ID_OBJ if not debug else env.GUILDS_ID_DEBUG_OBJ)

    #     @bot.event
    #     async def on_ready():
    #         print(f'{self._bot.user} has connected to Discord!')
    #         await self._bot.tree.sync()
    #         self._bot.tree.copy_global_to(guild=self.)
    #         await _bot.tree.sync(guild=settings.GUILDS_ID)
    #
    #     @bot.tree.command(description="Dota eh compromisso", nsfw=True)
    #     async def readycheck(ctx):
    #         await self.handle_poll()
    #
    #     @bot.tree.command()
    #     async def refresh(ctx):
    #         self.content = Content()
    #         self.fixed_hours = [int(x) for x in self.content.get("horarios")[0].split(',')]
    #
    # async def handle_poll(self):
    #     # role = ctx.guild.get_role()
    #     self.poll = Poll(self)
    #     await self.poll.start()
