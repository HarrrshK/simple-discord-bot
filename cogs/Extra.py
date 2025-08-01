import discord
from discord.ext import commands
from discord import app_commands
import sympy as sp
import re
import random

class Extra(commands.Cog):
    def __init__(self, bot):
        self.bot =  bot



    # Event handler for new messages
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author == self.bot.user:
            return
        
        
        math_expr_pattern = r'^[0-9+\-*/().\s]+$'

        if re.match(math_expr_pattern, message.content.strip()):
            
            await message.add_reaction('➕')

   
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        
        if payload.emoji.name == '➕' and payload.user_id != self.bot.user.id:
            # Get the channel and the message to which the reaction was added
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            # Check if the message contained a valid mathematical expression
            math_expr_pattern = r'^[0-9+\-*/().\s]+$'
            if re.match(math_expr_pattern, message.content.strip()):
                try:
                    # Evaluate the mathematical expression using sympy
                    result = sp.sympify(message.content.strip()).evalf()
                    # Respond with the answer
                    await channel.reply(f'{result}')
                except sp.SympifyError:
                    await channel.reply("Locha ho gaya boss jara sa!!!")

    @commands.command(name='purge')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, number: int):
        if number < 1:
            await ctx.send("Please specify a positive number of messages to delete.")
            return
        
        deleted = await ctx.channel.purge(limit=number)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Extra(bot))