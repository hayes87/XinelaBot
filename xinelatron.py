from typing import Any
import utils.env as env
import disnake
from disnake.ext import commands
from utils.content import Content


class XinelaTron(commands.Bot):
    def __init__(self, **options: Any):
        super().__init__(command_prefix='!', intents=disnake.Intents.all(), **options)
        self.content = Content()
        self.register_commands()
        self.run(env.BOT_TOKEN)

    def register_commands(self):
        @self.event
        async def on_ready():
            print(f'{self.user} has connected to Discord!')
            self.load_extension("cogs.poll")

