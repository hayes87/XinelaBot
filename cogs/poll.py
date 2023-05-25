import asyncio
import random
import traceback

import discord
from apscheduler.schedulers.base import STATE_STOPPED
from discord.ext import commands
import json

from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime, timedelta
import pytz
import os

from elevenlabs import generate, save
from elevenlabs import set_api_key
import utils.env as env
set_api_key(env.ELEVENLABS_API)


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
                "times": { "17h00": [], "18h00": [], "19h00": [], "20h00": [], "21h00": []},
                "jobs": []
            }

    def save_to_json(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.dict, file)

    def add(self, time: str, user_id: int):
        if time not in self.dict['times']:
            self.dict['times'][time] = []
        if user_id in self.dict['times'][time]:
            self.dict['times'][time].remove(user_id)
        else:
            self.dict['times'][time].append(user_id)
            self.dict['times'][time] = list(set(self.dict['times'][time]))
        self.save_to_json()
        return len(self.dict['times'][time])

    def add_timeslot(self, timeslot: str):
        if timeslot not in self.dict['times']:
            self.dict['times'][timeslot] = []
        self.save_to_json()

    def get_timeslots(self):
        return list(self.dict['times'].keys())

    def get_users_at_time(self, time):
        if time in self.dict['times']:
            return ', '.join(f'<@{user}>' for user in self.dict['times'][time])
        else:
            return "No users at this time."

    def get_users_list_at_time(self, time):
        if time in self.dict['times']:
            return list((user for user in self.dict['times'][time]))
        else:
            return None

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


class TimeslotModal(discord.ui.Modal, title="Novo horario"):
    hour = discord.ui.TextInput(style=discord.TextStyle.short, label="Hora (15h30)", required=True,
                                placeholder="19h30")

    async def on_submit(self, interaction: discord.Interaction):
        timeslot = f"{self.hour.value}"

        if len(timeslot.split("h")) == 2:
            try:
                hour, minute = map(int, timeslot.split("h"))
                if 0 <= hour < 24 and 0 <= minute < 60:
                    await self.view.add_timeslot(timeslot)
                    await interaction.response.send_message(f"Adicionei uma nova opcao {timeslot}.", ephemeral=True)
                else:
                    raise ValueError
            except ValueError:
                await interaction.response.send_message(f"Formato inválido! Use HHhMM.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Formato inválido! Use HHhMM.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        print(error)
        traceback.print_tb(error.__traceback__)


class TimeSlotButton(discord.ui.Button):
    def __init__(self, label, **kwargs):
        super().__init__(label=label, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await self.view.on_button(interaction, self.label)


# class TimeSlotRemoveButton(discord.ui.Button):
#     def __init__(self, label, **kwargs):
#         super().__init__(label=label, **kwargs)
#
#     async def callback(self, interaction: discord.Interaction):
#         time_select = TimeSlotSelect(self.view)
#         await interaction.message.edit(view=self.view)
#         await interaction.response.defer()
#         self.view.remove_item(time_select)

#
# class TimeSlotAddButton(discord.ui.Button):
#     def __init__(self, label, **kwargs):
#         super().__init__(label=label, **kwargs)
#
#     async def callback(self, interaction: discord.Interaction):
#         time_select = TimeSlotSelect(self.view)
#         await interaction.message.edit(view=self.view)
#         await interaction.response.defer()
#         self.view.remove_item(time_select)
#
#
# class TimeSlotSelect(discord.ui.Select):
#     view = None
#
#     def __init__(self, view):
#         self.view = view
#         options = []
#         for timeslot in self.view.data.get_timeslots():
#             options.append(discord.SelectOption(label=timeslot, value=timeslot))
#
#         super().__init__(options=options, placeholder="Selecione um horario")
#         self.view.add_item(self)
#
#     async def callback(self, interaction: discord.Interaction):
#         print("ACTION ")
#

class Dota2View(discord.ui.View):
    def __init__(self, user_id, loop, ctx, bot):
        super().__init__(timeout=18000)
        self.bot = bot
        self.ctx = ctx
        self.loop = loop
        self.message = None
        self.data = DataHandler()
        self.user_id = user_id
        self.scheduler = BackgroundScheduler()
        self.buttons = None

        if self.scheduler.state == STATE_STOPPED:
            self.scheduler.start()

    def create_buttons(self):
        if self.buttons is None:
            self.buttons = {}

        for timeslot in self.data.get_timeslots():
            print(timeslot)
            if timeslot in self.buttons:
                self.remove_item(self.buttons[timeslot])
            split_time = timeslot.split("h")
            timeslot_str = f"{split_time[0]}h"
            if split_time[1] != "00":
                timeslot_str += f"{split_time[1]}"
            button = TimeSlotButton(label=timeslot_str)
            self.add_item(button)
            self.buttons[timeslot] = button

        # if "+" in self.buttons:
        #     self.remove_item(self.buttons["+"])
        # button = TimeSlotAddButton(label="+")
        # self.add_item(button)
        # self.buttons["+"] = button
        #
        # if "-" in self.buttons:
        #     self.remove_item(self.buttons["-"])
        # button = TimeSlotRemoveButton(label="-")
        # self.add_item(button)
        # self.buttons["-"] = button

    async def new(self):

        self.create_buttons()
        embed = self.create_embed()

        try:
            role_id = int(os.getenv("ROLE_ID"))
        except:
            role_id = 0

        role = self.ctx.guild.get_role(role_id)
        if role:
            await self.ctx.send(f'{role.mention}!')
        else:
            print("role not found")

        self.message = await self.ctx.send(view=self, embed=embed)

        await self.wait()
        await self.disable_all_items()

    def create_embed(self):
        print("Updating Embed..")

        def get_button_style(time):
            if self.data.dict['times'].get(time) and self.user_id in self.data.dict['times'][time]:
                return discord.ButtonStyle.gray
            else:
                return discord.ButtonStyle.green

        embed = discord.Embed(title="Xinela Ready Checker", description="Escolha a hora do show!")

        embed.set_image(url="https://cdn.discordapp.com/attachments/1103077518375915571/1103541153724366868/image.png")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/1103071608005984360/a5ee3bf0eb26fd1629a99771d37c2780.png?size=256")

        for timeslot in self.data.get_timeslots():
            if self.data.dict['times'].get(timeslot):

                split_time = timeslot.split("h")
                timeslot_str = f"{split_time[0]}h"
                if split_time[1] != "00":
                    timeslot_str += f"{split_time[1]}"

                embed.add_field(inline=False, name=timeslot_str, value=self.data.get_users_at_time(timeslot))

            button = self.buttons.get(timeslot)
            if button is not None:
                button.style = get_button_style(timeslot)

        return embed

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def update_message(self):
        embed = self.create_embed()
        await self.message.edit(view=self, embed=embed)

    async def on_timeout(self) -> None:
        await self.disable_all_items()

    async def add_timeslot(self, timeslot):
        timeslot_formatted = self.format_time(timeslot)
        self.data.dict['times'][timeslot_formatted] = []
        self.data.save_to_json()
        self.create_buttons()
        await self.update_message()

    def format_time(self, time_str):
        split_time = time_str.split("h")
        hour = int(split_time[0]) if split_time[0] else 0
        minute = int(split_time[1]) if len(split_time) > 1 and split_time[1] else 0
        time_formatted = f"{hour:02d}h{minute:02d}"
        return time_formatted

    async def on_button(self, interaction, time_str):
        time_formatted = self.format_time(time_str)
        self.message = interaction.message
        await interaction.response.defer()
        count = self.data.add(time_formatted, interaction.user.id)
        job_id = f'reminder_{time_formatted}'
        existing_jobs = [job for job in self.data.dict['jobs'] if job['job_id'] == job_id]
        for job in existing_jobs:
            if self.scheduler.get_job(job['job_id']):
                self.scheduler.remove_job(job['job_id'])
                self.data.remove_job(job['job_id'])

        if count >= 5:
            split_time = time_str.split("h")
            hour = int(split_time[0])
            minute = int(split_time[1]) if len(split_time) > 1 and split_time[1] else 0
            run_date = datetime.now(pytz.timezone('America/Sao_Paulo'))
            run_date = run_date.replace(hour=hour - 1, minute=minute, second=0, microsecond=0)

            if run_date < datetime.now(pytz.timezone('America/Sao_Paulo')):
                run_date += timedelta(days=1)
            self.scheduler.add_job(self.sync_send_reminder, 'date', run_date=run_date, args=[time_formatted], id=job_id)
            self.data.add_job(run_date, interaction.channel.id, interaction.user.id, job_id)
        await self.update_message()

    def sync_send_reminder(self, selected_time):
        self.loop.create_task(self.send_reminder(selected_time))

    async def send_reminder(self, selected_time):
        ids = self.data.get_users_list_at_time(selected_time)
        # ids.extend([1103071608005984360, 1103071608005984360, 1103071608005984360, 1103071608005984360])

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

    # @discord.ui.button(label="Show Jobs", style=discord.ButtonStyle.primary)
    # async def on_button_show_jobs(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     # Get all jobs
    #     jobs = self.scheduler.get_jobs()
    #
    #     # Construct a string that lists all jobs and their run times
    #     job_list = "\n".join([f"Job ID: {job.id}, Run Time: {job.next_run_time}" for job in jobs])
    #
    #     # Create an embed with the job list
    #     embed = discord.Embed(title="Scheduled Jobs", description=job_list)
    #
    #     # Send the embed in the channel
    #     await interaction.response.send_message(embed=embed, ephemeral=True)
    #
    # @discord.ui.button(label="Remove All Jobs", style=discord.ButtonStyle.primary)
    # async def on_btn_remove_all_jobs(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     # Get all jobs
    #     self.scheduler.remove_all_jobs()
    #
    #     # Send the embed in the channel
    #     await interaction.response.send_message("Jobs Removed", ephemeral=True)
    #
    # @discord.ui.button(label="Dump DB", style=discord.ButtonStyle.primary)
    # async def on_button_dump_db(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     # Load the JSON file
    #     with open(self.data.json_file, 'r') as file:
    #         votes = json.load(file)
    #
    #     # Construct a string that lists all votes
    #     vote_list = "\n".join(
    #         [f"Time: {time}, User ID: {', '.join(map(str, user_ids))}" for time, user_ids in votes.items()])
    #
    #     # Create an embed with the vote list
    #     embed = discord.Embed(title="Votes DB Dump", description=vote_list)
    #
    #     # Send the embed in the channel
    #     await interaction.response.send_message(embed=embed, ephemeral=True)


class Poll(commands.Cog):
    def __init__(self, xinelabot):
        self._bot = xinelabot

    @commands.command()
    async def readycheck(self, ctx: commands.Context):
        view = Dota2View(user_id=ctx.author.id, loop=self._bot.loop, ctx=ctx, bot=self._bot)
        await view.new()

    # @commands.command()
    # async def anunciar_time(self, ctx):
    #     member_ids = [176479166856691714, 429398979717890080, 119832904388968451, 123603156574666752,
    #                   103533905486811136]
    #
    #     from utils import team_announce
    #     await team_announce.announce(ctx, self._bot.content.get("anuncio"), member_ids)
    #     frase = self._bot.content.get_random("abertura_frases")
    #     audio = generate(
    #         text=frase.replace("*", ""),
    #         voice=random.choice(["RpvoK8WoHsA3IVJ5sZRq"]),
    #         model="eleven_multilingual_v1"
    #     )
    #
    #     save(audio, "frase_do_dia.wav")
    #     with open("frase_do_dia.wav", "rb") as f:
    #         await ctx.send(file=discord.File(f, "frase_do_dia.wav"))


async def setup(bot):
    await bot.add_cog(Poll(bot))
