import asyncio
import random
import disnake
from disnake.ext import commands
from elevenlabs import generate, save
from elevenlabs import set_api_key
import utils.env as env
from dota.dota2View import Dota2View
from dota import team_announce
from disnake.ext import tasks
from datetime import datetime, timedelta

set_api_key(env.ELEVENLABS_API)


def async_to_sync(async_func):
    def wrapper(*args, **kwargs):
        return asyncio.create_task(async_func(*args, **kwargs))

    return wrapper


class Poll(commands.Cog):
    _bot = None

    def __init__(self, xinelabot):
        self._bot = xinelabot
        self.view = None

    @tasks.loop(hours=24)
    async def reset_loop(self):
        view = Dota2View(loop=self._bot.loop, bot=self._bot)
        view.data.reset()
        view.scheduler.remove_all_jobs()

    @reset_loop.before_loop
    async def before_reset_loop(self):
        now = datetime.now()
        midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        delta_s = (midnight - now).total_seconds()
        await asyncio.sleep(delta_s)

    @commands.slash_command(description="Marcar a hora da festa.")
    async def readycheck(self, interaction: disnake.ApplicationCommandInteraction):
        self.view = Dota2View(user_id=interaction.author.id, loop=self._bot.loop, ctx=interaction, bot=self._bot)
        await self.view.new()

    @commands.slash_command(description="Anuncia os vencedores.")
    async def anunciar(self, ctx: disnake.ApplicationCommandInteraction):
        if self.view is None:
            print("[Anunciar] View is none")
            return

        voted_time, unix_timestamp = self.view.data.most_votes()
        member_ids = self.view.data.get_users_list_at_time(voted_time)

        await self._anunciar(ctx, unix_timestamp, member_ids)

    @commands.command()
    async def test_anunciar_5(self, ctx: disnake.ApplicationCommandInteraction):
        member_ids = [89437921286819840, 89437921286819840, 89437921286819840, 89437921286819840, 89437921286819840]
        await self._anunciar(ctx, "1685750820", member_ids)

    async def _anunciar(self, ctx, timestamp, member_ids):
        if len(member_ids) <= 0:
            return

        await team_announce.create_team_photo(ctx, self._bot.content.get("anuncio"), member_ids)
        ids_str = ' '.join([f'<@{mid}>' for mid in member_ids])
        await ctx.send(f"Eis os escolhidos das <t:{timestamp}:t>! <t:{timestamp}:R>! \n {ids_str}")
        await ctx.send(file=disnake.File("group_photo.gif"))
        frase = self._bot.content.get_random("abertura_frases")
        audio = generate(
            text=frase.replace("*", ""),
            voice=random.choice(["RpvoK8WoHsA3IVJ5sZRq", "Josh", "Bella", "Adam"]),
            model="eleven_multilingual_v1"
        )
        save(audio, "sabedoria.wav")
        with open("sabedoria.wav", "rb") as f:
            await ctx.send(file=disnake.File(f, "sabedoria.wav"))

    @commands.slash_command(description="Reset a chamada")
    async def reset(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.send("Chamada resetada", ephemeral=True)
        view = Dota2View(user_id=ctx.author.id, loop=self._bot.loop, ctx=ctx, bot=self._bot)
        view.data.reset()
        view.scheduler.remove_all_jobs()


def setup(bot):
    bot.add_cog(Poll(bot))
