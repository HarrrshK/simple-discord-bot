import discord
from discord.ext import commands
from datetime import datetime
import re
import os


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot =  bot

    @commands.command(name='naam')
    async def naam(self, ctx, *, message: str = None):
        if not message and ctx.message.reference:
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            message = referenced_message.content

        if not message:
            await ctx.send("Please provide a list of user IDs or reply to a message containing them.")
            return

        # Extract user IDs from mentions using regex
        user_ids = re.findall(r'<@!?(\d+)>', message)
        usernames = []

        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(int(user_id))
                usernames.append(f"{user_id}: {user.name}")
            except discord.NotFound:
                usernames.append(f"{user_id}: Not Found")

        # Handle pagination
        pages = []
        page_size = 10  # Adjust as needed

        for i in range(0, len(usernames), page_size):
            page = usernames[i:i + page_size]
            embed = discord.Embed(title="Usernames from Mentions", color=discord.Color.blue())
            for username in page:
                user_id, name = username.split(": ", 1)
                embed.add_field(name=f"User ID: {user_id}", value=f"Username: {name}", inline=False)
            pages.append(embed)

        current_page = 0
        message = await ctx.send(embed=pages[current_page])

        if len(pages) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

        await message.add_reaction("📝")  # Note emoji for sending text file

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️", "📝"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=pages[current_page])
                elif str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                    current_page += 1
                    await message.edit(embed=pages[current_page])
                elif str(reaction.emoji) == "📝":
                    # Create a text file with all usernames
                    with open("usernames.txt", "w") as file:
                        file.write("\n".join(usernames))

                    # Send the text file
                    await ctx.send(file=discord.File("usernames.txt"))

                    # Delete the text file after sending
                    os.remove("usernames.txt")
                    break  # Stop listening after the note emoji is used

                await message.remove_reaction(reaction, user)

            except discord.errors.TimeoutError:
                break  # Stop if no reactions within the timeout period


            
async def setup(bot):
    await bot.add_cog(Test(bot))