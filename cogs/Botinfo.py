
import discord
from discord.ext import commands
from discord import Member, User
from typing import Optional, Union
import datetime
import requests
import platform

import datetime 
import time


CYAN_COLOR = 0x00FFFF

def format_uptime(uptime_seconds):
    return str(datetime.timedelta(seconds=uptime_seconds))

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  


    @commands.command(name="botinfo")
    async def display_bot_info(self, ctx):
        """Displays comprehensive information about the bot."""
        bot_user = self.bot.user
        total_guilds = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds)

        uptime_seconds = time.time() - self.start_time
        uptime = format_uptime(uptime_seconds)

        embed = discord.Embed(
            title=f"Information about {bot_user.name}",
            description="Here's a detailed summary of the bot's information.",
            color=CYAN_COLOR, 
        )

        embed.set_thumbnail(url=bot_user.avatar.url)

        embed.add_field(name="Bot Name", value=bot_user.name, inline=True)
        embed.add_field(name="Bot ID", value=bot_user.id, inline=True)
        embed.add_field(name="Servers", value=total_guilds, inline=True)
        embed.add_field(name="Total Members", value=total_members, inline=True)
        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py Version", value=discord.__version__, inline=True)

        bot_owner = self.bot.get_user(777614452186152991)  
        if bot_owner:
            embed.add_field(name="Bot Owner", value=f"{bot_owner.name}#{bot_owner.discriminator}", inline=True)
        else:
            embed.add_field(name="Bot Owner", value="HarsH", inline=True)


        embed.set_footer(text="Developed by HarsH.", icon_url=bot_user.avatar.url)

        await ctx.reply(embed=embed)


        

async def setup(bot):
    await bot.add_cog(BotInfo(bot))