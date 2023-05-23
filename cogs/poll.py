import asyncio
import random

import discord
from apscheduler.schedulers.base import STATE_STOPPED
from discord.ext import commands
import json

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta
import pytz
import os

from elevenlabs import generate, play, save
from elevenlabs import set_api_key

set_api_key("335dab30fb1997ab03bc18c970d146fd")


class DataHandler:
    def __init__(self, json_file='Data.json'):
        self.json_file = json_file
        self.dict = self.load_from_json()

    def load_from_json(self):
        if os.path.isfile(self.json_file):
            with open(self.json_file) as file:
                return json.load(file)
        else:
            return {
                "times": {"18h": [], "19h": [], "20h": [], "21h": []},
                "jobs": []
            }

    def save_to_json(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.dict, file)

    def add(self, time: str, user_id: int):
        if user_id in self.dict['times'][time]:
            self.dict['times'][time].remove(user_id)
        else:
            self.dict['times'][time].append(user_id)
            self.dict['times'][time] = list(set(self.dict['times'][time]))
        self.save_to_json()
        return len(self.dict['times'][time])

    def get_users_at_time(self, time):
        if time in self.dict['times']:
            return ', '.join(f'<@{user}>' for user in self.dict['times'][time])
        else:
            return "No users at this time."

    def add_job(self, run_date, channel_id, user_id, job_id):
        self.dict['jobs'].append({
            'job_id': job_id,
            'run_time': run_date.isoformat(),
            'user_id': user_id,
            'channel_id': channel_id
        })
        self.save_to_json()

    def remove_job(self, job_id):
        self.dict['jobs'] = [job for job in self.dict['jobs'] if job['job_id'] != job_id]
        self.save_to_json()


def async_to_sync(async_func):
    def wrapper(*args, **kwargs):
        return asyncio.create_task(async_func(*args, **kwargs))

    return wrapper


class Dota2View(discord.ui.View):
    def __init__(self, user_id, loop, ctx, bot):
        super().__init__(timeout=18000)
        self.bot = bot
        self.ctx = ctx
        self.loop = loop
        self.message = None
        self.data = DataHandler()  # Using the new DataHandler
        self.user_id = user_id
        self.scheduler = BackgroundScheduler()

        if self.scheduler.state == STATE_STOPPED:
            self.scheduler.start()

    async def new(self):
        embed = self.create_embed()
        self.message = await self.ctx.send(view=self, embed=embed)
        await self.wait()
        await self.disable_all_items()

    def create_embed(self):
        embed = discord.Embed(title="Xinela Ready Checker", description="Escolha a hora do show!")

        # embed.set_image(url="https://cdn.discordapp.com/attachments/1103077518375915571/1103541153724366868/image.png")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/1103071608005984360/a5ee3bf0eb26fd1629a99771d37c2780.png?size=256")

        def get_button_style(time):
            if self.data.dict['times'].get(time) and self.user_id in self.data.dict['times'][time]:
                return discord.ButtonStyle.gray
            else:
                return discord.ButtonStyle.green

        self.children[0].style = get_button_style("18h")
        self.children[1].style = get_button_style("19h")
        self.children[2].style = get_button_style("20h")
        self.children[3].style = get_button_style("21h")

        if self.data.dict['times'].get("18h"):
            embed.add_field(inline=False, name="18H", value=self.data.get_users_at_time("18h"))
        if self.data.dict['times'].get("19h"):
            embed.add_field(inline=False, name="19H", value=self.data.get_users_at_time("19h"))
        if self.data.dict['times'].get("20h"):
            embed.add_field(inline=False, name="20H", value=self.data.get_users_at_time("20h"))
        if self.data.dict['times'].get("21h"):
            embed.add_field(inline=False, name="21H", value=self.data.get_users_at_time("21h"))

        return embed

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def update_message(self):
        embed = self.create_embed()
        await self.message.edit(view=self, embed=embed)

    async def on_timeout(self) -> None:
        await self.message.channel.send("Timedout")
        await self.disable_all_items()

    @discord.ui.button(label="18H", style=discord.ButtonStyle.green)
    async def on_button_18h(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._on_button(interaction, 18)

    @discord.ui.button(label="19H", style=discord.ButtonStyle.green)
    async def on_button_19h(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._on_button(interaction, 19)

    @discord.ui.button(label="20H", style=discord.ButtonStyle.green)
    async def on_button_20h(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._on_button(interaction, 20)

    @discord.ui.button(label="21H", style=discord.ButtonStyle.green)
    async def on_button_21h(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._on_button(interaction, 21)

    async def _on_button(self, interaction, time):
        self.message = interaction.message
        await interaction.response.defer()
        count = self.data.add(f"{time}h", interaction.user.id)
        job_id = f'reminder_{time}h'
        existing_jobs = [job for job in self.data.dict['jobs'] if job['job_id'] == job_id]
        for job in existing_jobs:
            if self.scheduler.get_job(job['job_id']):
                self.scheduler.remove_job(job['job_id'])
                self.data.remove_job(job['job_id'])

        if count >= 1:
            run_date = datetime.now(pytz.timezone('America/Sao_Paulo'))
            # run_date = run_date.replace(hour=time - 1, minute=0, second=0, microsecond=0)
            run_date += timedelta(seconds=5)

            if run_date < datetime.now(pytz.timezone('America/Sao_Paulo')):
                run_date += timedelta(days=1)
            self.scheduler.add_job(self.sync_send_reminder, 'date', run_date=run_date, args=["18h"], id=job_id)
            self.data.add_job(run_date, interaction.channel.id, interaction.user.id, job_id)
        await self.update_message()

    def sync_send_reminder(self, selected_time):
        self.loop.create_task(self.send_reminder(selected_time))

    async def send_reminder(self, selected_time):
        # ids = self.data.get_users_at_time(selected_time)
        ids = [89437921286819840, 89437921286819840, 89437921286819840, 89437921286819840, 89437921286819840,
               89437921286819840, 89437921286819840]
        from utils import team_announce
        await team_announce.announce(self.ctx, self.bot.content.get("anuncio"), ids)
        frase = self.bot.content.get_random("abertura_frases")
        audio = generate(
            text=frase.replace("*", ""),
            voice=random.choice(["RpvoK8WoHsA3IVJ5sZRq"]),
            model="eleven_multilingual_v1"
        )

        save(audio, "frase_do_dia.wav")
        with open("frase_do_dia.wav", "rb") as f:
            await self.message.channel.send(file=discord.File(f, "frase_do_dia.wav"))

        # await self.message.channel.send(frase)

    @discord.ui.button(label="Show Jobs", style=discord.ButtonStyle.primary)
    async def on_button_show_jobs(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get all jobs
        jobs = self.scheduler.get_jobs()

        # Construct a string that lists all jobs and their run times
        job_list = "\n".join([f"Job ID: {job.id}, Run Time: {job.next_run_time}" for job in jobs])

        # Create an embed with the job list
        embed = discord.Embed(title="Scheduled Jobs", description=job_list)

        # Send the embed in the channel
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Remove All Jobs", style=discord.ButtonStyle.primary)
    async def on_btn_remove_all_jobs(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get all jobs
        self.scheduler.remove_all_jobs()

        # Send the embed in the channel
        await interaction.response.send_message("Jobs Removed", ephemeral=True)


@discord.ui.button(label="Dump DB", style=discord.ButtonStyle.primary)
async def on_button_dump_db(self, interaction: discord.Interaction, button: discord.ui.Button):
    # Load the JSON file
    with open(self.data.json_file, 'r') as file:
        votes = json.load(file)

    # Construct a string that lists all votes
    vote_list = "\n".join(
        [f"Time: {time}, User ID: {', '.join(map(str, user_ids))}" for time, user_ids in votes.items()])

    # Create an embed with the vote list
    embed = discord.Embed(title="Votes DB Dump", description=vote_list)

    # Send the embed in the channel
    await interaction.response.send_message(embed=embed, ephemeral=True)


class Poll(commands.Cog):
    def __init__(self, xinelabot):
        self._bot = xinelabot

    @commands.command()
    async def play(self, ctx: commands.Context):
        view = Dota2View(user_id=ctx.author.id, loop=self._bot.loop, ctx=ctx, bot=self._bot)
        await view.new()

    # if self.has_active_poll():
    #   await ctx.send(f"Isso ja foi postado.")
    #  return

    # self.fixed_hours = [int(x) for x in self._bot.content.get("horarios")[0].split(',')]
    # time_options = get_unix_timestamps(self.fixed_hours)
    # time_entries = []

    # Abertura
    # await ctx.send(f"<@{self._bot.role_id}>")
    # await ctx.send(self._bot.content.get_random("abertura_imagens"))
    # await ctx.send(self._bot.content.get_random("abertura_frases"))
    #
    # # Options
    # for time_option in time_options:
    #     message = await ctx.send(f"Vote para jogar às <t:{time_option}:t>.")
    #     await message.add_reaction('✅')
    #     time_entries.append(TimeEntry(time_option, message.id))

    # await self.anunciar_time(ctx)

    # def has_active_poll(self):
    #     if Path("lock").exists():
    #         with open("lock", "r") as f:
    #             self.poll_channel_id, self.poll_message_id, self.start_time, self.reset_time = map(float,
    #                                                                                                f.readline().split())
    #     else:
    #         self.poll_channel_id, self.poll_message_id, self.start_time, self.reset_time = None, None, None, None
    #
    @commands.command()
    async def anunciar_time(self, ctx):
        member_ids = [89437921286819840, 89437921286819840, 89437921286819840, 89437921286819840,
                      89437921286819840, 89437921286819840, 89437921286819840]

        from utils import team_announce
        await team_announce.announce(ctx, self._bot.content.get("anuncio"), member_ids)
        frase = self._bot.content.get_random("abertura_frases")
        audio = generate(
            text=frase.replace("*", ""),
            voice=random.choice(["RpvoK8WoHsA3IVJ5sZRq"]),
            model="eleven_multilingual_v1"
        )

        save(audio, "frase_do_dia.wav")
        with open("frase_do_dia.wav", "rb") as f:
            await ctx.send(file=discord.File(f, "frase_do_dia.wav"))


async def setup(bot):
    await bot.add_cog(Poll(bot))
