import discord
from discord.ext import commands, tasks
import os
import config
import asyncio
from itertools import cycle
import json
from pretty_help import PrettyHelp




def get_server_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    return prefix[str(message.guild.id)]


intents = discord.Intents.all()

bot = commands.Bot(command_prefix=get_server_prefix, intents=intents, case_insensitive=True, help_command=PrettyHelp(color=0x00ff00, ending_note="Have fun!", sort_commands=True))



@bot.event
async def on_ready():
    game = discord.Game("Santōryū: Sanzen Sekai")
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print(f'Logged in as {bot.user.name}')



@bot.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(guild.id)] = "^"

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)


@bot.command()
async def setprefix(ctx, *, newprefix: str):
    with open("prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(ctx.guild.id)] = newprefix

    with open("prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)



async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} is loaded")



async def main():
    async with bot:
        await load()
        await bot.start(config.TOKEN)


asyncio.run(main())