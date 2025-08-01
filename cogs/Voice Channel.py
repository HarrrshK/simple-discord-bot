import discord
from discord.ext import commands
from pretty_help import PrettyHelp

# Create a check to determine if the user has admin permissions
def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

class VoiceChannel(commands.Cog):
    """
Manages the Voice Channel
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Voice Channel.py is loaded")


    @commands.command(name='disconnectall', aliases=['dca', 'disconnectusers','disconnecteveryone',])
    @commands.check(is_admin)  # Restrict the command to admins
    async def dca(self, ctx):
        """
        Disconnects all non-bot users from the author's voice channel.
            
        Aliases: 'disconnectall', 'disconnect_users'
        """
        # Ensure the author is in a voice channel
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.reply("You need to be in a voice channel to use this command.")
            return

        voice_channel = ctx.author.voice.channel
        disconnected_users = []

        # Disconnect non-bot users from the voice channel
        for member in voice_channel.members:
            if not member.bot:
                await member.move_to(None)  # Disconnect the member
                disconnected_users.append(member.display_name)

        # Send a message with the list of disconnected users
        if disconnected_users:
            await ctx.reply(f"Disconnected users: {', '.join(disconnected_users)}")
        else:
            await ctx.reply("No users to disconnect in this voice channel.")

    @commands.command(name='drag', aliases=['move','transfer'])
    @commands.check(is_admin)  # Restrict the command to admins
    async def move_all_to(self, ctx, target_channel_id: int):
        """
        Moves all non-bot users from the author's voice channel to the specified voice channel.
        """
        # Get the target voice channel from the provided ID
        target_channel = ctx.guild.get_channel(target_channel_id)

        # Validate that the target channel exists and is a voice channel
        if target_channel is None or not isinstance(target_channel, discord.VoiceChannel):
            await ctx.reply("Invalid voice channel ID. Please provide a valid voice channel ID.")
            return

        # Get the author's current voice channel
        author_channel = ctx.author.voice.channel if ctx.author.voice else None
        if author_channel is None:
            await ctx.reply("You need to be in a voice channel to use this command.")
            return

        # Move all members from the author's voice channel to the target voice channel
        moved_users = []
        for member in author_channel.members:
            if not member.bot:  # Optionally exclude bots from being moved
                await member.move_to(target_channel)
                moved_users.append(member.display_name)

        # Send a message indicating which users were moved
        if moved_users:
            await ctx.reply(f"Moved users to {target_channel.name}: {', '.join(moved_users)}")
        else:
            await ctx.reply("No users to move in your voice channel.")

    # Command to ban a user from all voice channels
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def vcban(self, ctx, user: discord.Member):
        # Loop through all voice channels in the guild
        for channel in ctx.guild.voice_channels:
            # Set view permissions to False for the user
            await channel.set_permissions(user, view_channel=False)

        await ctx.send(f"{user.display_name} has been banned from all voice channels.")

    # Command to unban a user from all voice channels
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def vcunban(self, ctx, user: discord.Member):
        # Loop through all voice channels in the guild
        for channel in ctx.guild.voice_channels:
            # Remove specific permission overrides for the user
            await channel.set_permissions(user, overwrite=None)

        await ctx.send(f"{user.display_name} has been unbanned from all voice channels.")

    @commands.command(name='dca')
    @commands.check(is_admin)  # Restrict the command to admins
    async def dca(self, ctx):
        # Ensure the author is in a voice channel
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.reply("You need to be in a voice channel to use this command.")
            return
        
        voice_channel = ctx.author.voice.channel
        disconnected_users = []
        
        # Disconnect non-bot users from the voice channel
        for member in voice_channel.members:
            if not member.bot:
                await member.move_to(None)  # Disconnect the member
                disconnected_users.append(member.display_name)

        # Send a message with the list of disconnected users
        if disconnected_users:
            await ctx.reply(f"Disconnected users: {', '.join(disconnected_users)}")
        else:
            await ctx.reply("No users to disconnect in this voice channel.")


    @commands.command(name='drag')
    @commands.check(is_admin)  # Restrict the command to admins
    async def move_all_to(self, ctx, target_channel_id: int):
        # Get the target voice channel from the provided ID
        target_channel = ctx.guild.get_channel(target_channel_id)

        # Validate that the target channel exists and is a voice channel
        if target_channel is None or not isinstance(target_channel, discord.VoiceChannel):
            await ctx.reply("Invalid voice channel ID. Please provide a valid voice channel ID.")
            return

        # Get the author's current voice channel
        author_channel = ctx.author.voice.channel if ctx.author.voice else None
        if author_channel is None:
            await ctx.reply("You need to be in a voice channel to use this command.")
            return

        # Move all members from the author's voice channel to the target voice channel
        moved_users = []
        for member in author_channel.members:
            if not member.bot:  # Optionally exclude bots from being moved
                await member.move_to(target_channel)
                moved_users.append(member.display_name)

        # Send a message indicating which users were moved
        if moved_users:
            await ctx.reply(f"Moved users to {target_channel.name}: {', '.join(moved_users)}")
        else:
            await ctx.reply("No users to move in your voice channel.")

async def setup(bot):
    await bot.add_cog(VoiceChannel(bot))