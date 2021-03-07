import os
from datetime import datetime

import discord
from discord.ext import commands
from pretty_help import PrettyHelp

start_time = datetime.utcnow()


description = """
PyBot - A Bot for PyBot
"""
bot = commands.Bot(
    command_prefix=["!", ">", "."],
    owner_ids={747451011484090479, 727365670395838626},
    intents=discord.Intents.all(),
    help_command=PrettyHelp(),
    description=description,
    case_insensitive=True,
    start_time=start_time,
)


@bot.event
async def on_ready():
    print("Bot is ready")


"""
Loads cog
"""
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.load_extension("jishaku")


token = os.environ.get("TOKEN")


bot.run(f"{token}")
