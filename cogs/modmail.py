import os

import discord
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown

allowed_roles = [
    790221089786822657,
    795937707263000596,
    790219985229709342,
    794402650569310239,
]


class ModMail(commands.Cog):
    """
    Commands related to ModMail
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("ModMail Cog Loaded Succesfully")

    @commands.command(cooldown_after_parsing=True)
    @cooldown(1, 21600, BucketType.user)
    async def report(
        self, ctx: commands.Context, member: discord.Member, *, reason: str
    ):
        """
        Report a member
        """
        if len(reason) < 100:

            guild = ctx.guild
            if member == self.bot.user:
                await ctx.send("**It is me!**")

            elif guild.me.top_role < member.top_role:
                await ctx.send("**Person is above me in roles.**")
            elif member.bot:
                await ctx.send("**You cannot report bot**")
            elif member == ctx.author:
                await ctx.send("**You cannot report yourself**")
            else:

                report_channel = self.bot.get_channel(813688372589363212)
                embed = discord.Embed(
                    title=f"{ctx.author.name} Reported {member.name}",
                    description=f"Reporter id -> {ctx.author.id}\nReported id -> {member.id}\nReason ->\n{reason}",
                    color=0xFF00FF,
                )
                await ctx.message.delete()
                await ctx.send(f"**Reported {member.name}**")
                await report_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(ModMail(bot))
