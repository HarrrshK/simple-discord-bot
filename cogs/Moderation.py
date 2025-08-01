import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import datetime

# Helper function to create a mute role if it doesn't exist
async def get_or_create_mute_role(guild):
    role = discord.utils.get(guild.roles, name="Muted")
    if not role:
        # Create the role with no permissions to speak, send messages, etc.
        role = await guild.create_role(
            name="Muted",
            permissions=discord.Permissions(
                send_messages=False,
                speak=False
            ),
            reason="Created 'Muted' role for moderation purposes"
        )
        # Apply the role's restrictions to all text and voice channels
        for channel in guild.channels:
            await channel.set_permissions(
                role, send_messages=False, speak=False
            )
    return role


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warned_users = {}  # Dictionary to track user warnings
        self.permissions_backup = {}

        
    @commands.command(name="kick", help="Kick a user from the server")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked from the server for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="ban", help="Ban a user from the server")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="unban", help="Unban a user from the server")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, user: str):
        # Get the list of banned users
        banned_users = await ctx.guild.bans()  # Corrected to properly await the coroutine
        
        # Extract name and discriminator
        member_name, member_discriminator = user.split("#")
        
        # Loop through the banned users to find the one to unban
        for banned_entry in banned_users:
            if (banned_entry.user.name == member_name and 
                banned_entry.user.discriminator == member_discriminator):
                await ctx.guild.unban(banned_entry.user)
                await ctx.send(f"Unbanned {banned_entry.user.mention}")
                return
        
        # If user wasn't found in the ban list
        await ctx.send(f"User {user} not found in the ban list.")

    @commands.command(name="mute", help="Mute a user in the server")
    @has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            mute_role = await get_or_create_mute_role(ctx.guild)
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"{member.mention} has been muted for: {reason}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to mute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(name="warn", help="Warn a user in the server")
    @has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        # Log the warning
        if member.id not in self.warned_users:
            self.warned_users[member.id] = []
        self.warned_users[member.id].append(reason)
        
        # Notify the user
        try:
            await member.send(f"You have been warned in {ctx.guild.name} for: {reason}")
        except discord.Forbidden:
            # If we can't send DMs, ignore it
            pass
        
        await ctx.send(f"{member.mention} has been warned for: {reason}")

    @commands.command(name="unmute", help="Unmute a user in the server")
    @has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            mute_role = await get_or_create_mute_role(ctx.guild)
            await member.remove_roles(mute_role, reason=reason)
            await ctx.send(f"{member.mention} has been unmuted.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unmute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


    @commands.command(name="hrole", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def hide_role(self, ctx):
        role_id = 1260532968431161425
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send("Role not found.")
            return
        
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(role, view_channel=False)
        
        await ctx.send(f"{role.name} hidden in all channels.")

    @commands.command(name="srole", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def show_role(self, ctx):
        role_id = 1260532968431161425
        role = ctx.guild.get_role(role_id)
        
        if not role:
            await ctx.send("Role not found.")
            return
        
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(role, overwrite=None)
        
        await ctx.send(f" {role.name} wait non hidden in all channel")

async def setup(bot):
    await bot.add_cog(Moderation(bot))