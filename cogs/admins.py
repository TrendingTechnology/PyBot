import os

import discord
from discord.ext import commands

admins = [747451011484090479, 727365670395838626]


class Admins(commands.Cog):
    """
    Commands related to admins
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admins cog loaded successfully")

    @commands.command(description="Load cog")
    async def load(self, ctx, extension):
        """
        Load cog
        """
        if ctx.author.id not in admins:
            self.bot.load_extension(f"cogs.{extension}")
            await ctx.send("Done")

    @commands.command(description="Unload cog")
    async def unload(self, ctx, extension):
        """
        Unload Cog
        """
        if ctx.author.id not in admins:
            self.bot.unload_extension(f"cogs.{extension}")
            await ctx.send("Done")

    @commands.command(description="Reload cog")
    async def reload(self, ctx, extension):
        """
        Reload Cog
        """
        if ctx.author.id not in admins:
            self.bot.unload_extension(f"cogs.{extension}")
            self.bot.load_extension(f"cogs.{extension}")
            await ctx.send("Done")


def setup(bot):
    bot.add_cog(Admins(bot))
