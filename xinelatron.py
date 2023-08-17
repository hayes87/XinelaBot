from typing import Any
import utils.env as env
import disnake
from disnake.ext import commands
from utils.content import Content


class XinelaTron(commands.Bot):
    def __init__(self, **options: Any):
        print("Initializing...")
        super().__init__(command_prefix='!', intents=disnake.Intents.all(), **options)
        print("Creating Content")
        self.content = Content()
        print("Registering Commands")
        self.register_commands()
        print("Starting...")
        self.run(env.BOT_TOKEN)

    def register_commands(self):
        @self.event
        async def on_ready():
            print(f'{self.user} has connected to Discord!')
            self.load_extension("cogs.poll")

