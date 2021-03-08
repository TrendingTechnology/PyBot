import difflib
import re
import unicodedata
from datetime import datetime
from typing import Tuple, Union
import discord
from discord import Colour, Embed, utils
from discord.ext import commands
from discord.ext.commands import (
    BadArgument,
    BucketType,
    Cog,
    Context,
    clean_content,
    command,
    cooldown,
    has_any_role,
)
from discord.utils import snowflake_time

from utils.messages import send_denial
from utils.paginator import LinePaginator

DESCRIPTIONS = ("Command processing time", "Discord API latency")
ROUND_LATENCY = 3

import aiohttp
from discord import AsyncWebhookAdapter, Webhook

ZEN_OF_PYTHON = """\
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
"""


class Info(commands.Cog):
    """ Commands related to information """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Info Cog Loaded Succesfully")

    @commands.command()
    async def bot(sef, ctx):
        """
        Shows info about bot
        """
        e = discord.Embed(color=0x00FFCC)
        e.set_author(name="Bot statistics", icon_url=ctx.author.avatar_url)
        e.add_field()

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """
        Gets different measures of latency within the bot.
        Returns bot, Discord Protocol latency.
        """
        # datetime.datetime objects do not have the "milliseconds" attribute.
        # It must be converted to seconds before converting to milliseconds.
        bot_ping = (datetime.utcnow() - ctx.message.created_at).total_seconds() * 1000
        bot_ping = f"{bot_ping:.{ROUND_LATENCY}f} ms"

        # Discord Protocol latency return value is in seconds, must be multiplied by 1000 to get milliseconds.
        discord_ping = f"{self.bot.latency * 1000:.{ROUND_LATENCY}f} ms"

        embed = Embed(title="Pong!", color=0x00FFCC)

        for desc, latency in zip(DESCRIPTIONS, [bot_ping, discord_ping]):
            embed.add_field(name=desc, value=latency, inline=False)

        await ctx.reply(embed=embed)

    @commands.command()
    async def charinfo(self, ctx, *, characters):
        """Shows you information on up to 50 unicode characters."""
        match = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if match:
            return await send_denial(
                ctx,
                "**Non-Character Detected**\n"
                "Only unicode characters can be processed, but a custom Discord emoji "
                "was found. Please remove it and try again.",
            )

        if len(characters) > 50:
            return await send_denial(ctx, f"Too many characters ({len(characters)}/50)")

        def get_info(char: str) -> Tuple[str, str]:
            digit = f"{ord(char):x}"
            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"
            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            info = f"`{u_code.ljust(10)}`: {name} - {utils.escape_markdown(char)}"
            return info, u_code

        char_list, raw_list = zip(*(get_info(c) for c in characters))
        embed = Embed().set_author(name="Character Info")

        if len(characters) > 1:
            # Maximum length possible is 502 out of 1024, so there's no need to truncate.
            embed.add_field(
                name="Full Raw Text", value=f"`{''.join(raw_list)}`", inline=False
            )

        await LinePaginator.paginate(
            char_list, ctx, embed, max_lines=10, max_size=2000, empty=False
        )

    @commands.command(hidden=True)
    async def codeblock(self, ctx):
        embed = discord.Embed(title="CodeBlocks", color=0xFF0000)
        embed.set_image(url="https://i.imgur.com/va1dpTv.png")
        embed.set_footer(text="**These are backticks**, not quotes.")
        await ctx.reply(embed=embed)

    @commands.command()
    async def zen(
        self, ctx: Context, *, search_value: Union[int, str, None] = None
    ) -> None:
        """
        Show the Zen of Python.
        Without any arguments, the full Zen will be produced.
        If an integer is provided, the line with that index will be produced.
        If a string is provided, the line which matches best will be produced.
        """
        embed = Embed(
            colour=Colour.blurple(),
            title="The Zen of Python",
            description=ZEN_OF_PYTHON,
        )

        if search_value is None:
            embed.title += ", by Tim Peters"
            await ctx.send(embed=embed)
            return

        zen_lines = ZEN_OF_PYTHON.splitlines()

        # handle if it's an index int
        if isinstance(search_value, int):
            upper_bound = len(zen_lines) - 1
            lower_bound = -1 * upper_bound
            if not (lower_bound <= search_value <= upper_bound):
                raise BadArgument(
                    f"Please provide an index between {lower_bound} and {upper_bound}."
                )

            embed.title += f" (line {search_value % len(zen_lines)}):"
            embed.description = zen_lines[search_value]
            await ctx.send(embed=embed)
            return

        # Try to handle first exact word due difflib.SequenceMatched may use some other similar word instead
        # exact word.
        for i, line in enumerate(zen_lines):
            for word in line.split():
                if word.lower() == search_value.lower():
                    embed.title += f" (line {i}):"
                    embed.description = line
                    await ctx.send(embed=embed)
                    return

        # handle if it's a search string and not exact word
        matcher = difflib.SequenceMatcher(None, search_value.lower())

        best_match = ""
        match_index = 0
        best_ratio = 0

        for index, line in enumerate(zen_lines):
            matcher.set_seq2(line.lower())

            # the match ratio needs to be adjusted because, naturally,
            # longer lines will have worse ratios than shorter lines when
            # fuzzy searching for keywords. this seems to work okay.
            adjusted_ratio = (len(line) - 5) ** 0.5 * matcher.ratio()

            if adjusted_ratio > best_ratio:
                best_ratio = adjusted_ratio
                best_match = line
                match_index = index

        if not best_match:
            raise BadArgument(
                "I didn't get a match! Please try again with a different search term."
            )

        embed.title += f" (line {match_index}):"
        embed.description = best_match
        await ctx.send(embed=embed)


def setup(bot) -> None:
    """Load the Latency cog."""
    bot.add_cog(Info(bot))
