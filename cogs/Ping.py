import discord
from discord.ext import commands
from pretty_help import PrettyHelp

# Create a check to determine if the user has admin permissions
def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

class Ping(commands.Cog):
    """
    Ping cog provides commands for managing voice channels and checking bot latency.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py is loaded")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Check the bot's latency.
        
        This command retrieves the bot's latency in milliseconds and displays it in a yellow embed.
        """
        latency = round(self.bot.latency * 1000)  # Get bot's latency in milliseconds
        embed = discord.Embed(
            title="Ping",
            description=f"```Latency: {latency}ms```",
            color=discord.Color.gold()  # Set the embed color to yellow
        )
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Ping(bot))