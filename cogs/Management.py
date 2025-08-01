
import discord
from discord.ext import commands
from discord import Member, User
from typing import Optional, Union
from datetime import datetime

# Create a check to determine if the user has admin permissions
def is_admin(ctx):
    return ctx.author.guild_permissions.administrator



def get_total_members(bot):
    total_members = 0
    for guild in bot.guilds:
        total_members += guild.member_count
    return total_members

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot =  bot
        self.original_permissions = {}
        self.deleted_messages = {}


    @commands.command(
        name="userinfo",
        aliases=["whois", "ui"],
        usage="Userinfo [user]"
    )
    @commands.guild_only()
    async def userinfo(self, ctx, member: Optional[Union[Member, User]] = None):
        member = member or ctx.author

        if member not in ctx.guild.members:
            try:
                member = await self.bot.fetch_user(member.id)
            except discord.NotFound:
                return await ctx.send("User not found.")

        embed = discord.Embed(color=0x2f3136)
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(
            name=f"{member.name}'s Information",
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url
        )
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        embed.add_field(
            name="__General Information__",
            value=f"""
    **Name:** {member}
    **ID:** {member.id}
    **Bot?:** {'<:GreenTick:1018174649198202990> Yes' if member.bot else '<:no_badge:1073853728764985385> No'}
    **Account Created:** <t:{round(member.created_at.timestamp())}:R>
    """
        )

        if member in ctx.guild.members:
            roles = member.roles[1:][::-1]  # Exclude @everyone role
            roles_mention = ", ".join(role.mention for role in roles) if roles else "None"
            roles_count = f"{len(roles)}" if roles else "0"
            highest_role = roles[0].mention if roles else "None"
            color = member.color or discord.Color.default()

            role_info = (
                f"**Highest Role:** {highest_role}\n"
                f"**Roles [{roles_count}]:** {roles_mention if len(roles_mention) <= 1024 else roles_mention[0:1006] + ' and more...'}\n"
                f"**Color:** {color}"
            )

            embed.add_field(
                name="__Role Info__",
                value=role_info,
                inline=False
            )

        await ctx.reply(embed=embed)
        await ctx.reply(f"{member}")
        
    # Lockdown command to remove "view channel" permissions from everyone in all channels
    @commands.command(name='lockdown')
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        guild = ctx.guild
        
        # Save current permissions for each channel
        self.original_permissions = {
            channel.id: channel.overwrites
            for channel in guild.channels
        }
        
        # Remove "view channel" permissions for @everyone in all channels
        for channel in guild.channels:
            overwrites = channel.overwrites_for(guild.default_role)
            overwrites.update(read_messages=False)  # For text channels
            overwrites.update(connect=False)        # For voice channels
            await channel.set_permissions(guild.default_role, overwrite=overwrites)
        
        await ctx.reply("Server is now in lockdown.")

    # Unlockdown command to restore permissions to their original state
    @commands.command(name='unlockdown')
    @commands.has_permissions(administrator=True)
    async def unlockdown(self, ctx):
        guild = ctx.guild
        
        if not self.original_permissions:
            await ctx.send("No previous lockdown state found. Cannot unlock.")
            return
        
        # Restore the original permissions for each channel
        for channel in guild.channels:
            if channel.id in self.original_permissions:
                original_overwrite = self.original_permissions[channel.id].get(
                    guild.default_role, discord.PermissionOverwrite()
                )
                await channel.set_permissions(guild.default_role, overwrite=original_overwrite)
        
        await ctx.reply("Server is now unlocked.")


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return  # Ignore messages from bots
        
        # Store the deleted message details
        message_data = {
            'content': message.content,
            'author': str(message.author),
            'timestamp': message.created_at,
            'attachments': [attachment.url for attachment in message.attachments],
            'embeds': message.embeds,
        }
        
        self.deleted_messages[message.channel.id] = message_data

    @commands.command(name='snipe')
    async def snipe(self, ctx):
        if ctx.channel.id not in self.deleted_messages:
            await ctx.reply("There's nothing to snipe in this channel.")
            return
        
        # Retrieve the last deleted message data
        deleted_message = self.deleted_messages[ctx.channel.id]
        
        embed = discord.Embed(
            title="Sniped Message",
            description=deleted_message['content'] or "(No text content)",
            color=discord.Color.blue(),
            timestamp=deleted_message['timestamp']
        )
        
        embed.set_footer(text=f"Deleted by: {deleted_message['author']}")

        # Add attachments to the embed
        for attachment in deleted_message['attachments']:
            embed.add_field(name="Attachment", value=attachment, inline=False)

        # Add embeds if they existed in the deleted message
        for message_embed in deleted_message['embeds']:
            embed.add_field(name="Embed", value=str(message_embed.to_dict()), inline=False)

        await ctx.reply(embed=embed)



    @commands.command(name='lock')
    async def lock_channel(self, ctx, target_channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.reply("You do not have the manage_channels permission.")

        channel = target_channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        overwrite.view_channel = False  # Remove view permission
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply(f"{channel.mention} has been locked.")

    @commands.command(name='unlock')
    async def unlock_channel(self, ctx, target_channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.reply("You do not have the manage_channels permission.")

        channel = target_channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        overwrite.view_channel = True  # Restore view permission
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply(f"{channel.mention} has been unlocked.")

    @commands.command(name='dchannel', help='Delete mentioned channel or current channel if not mentioned')
    async def delete_channel(self, ctx, target_channel: discord.TextChannel = None):
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.reply("You do not have the manage_channels permission.")

        if target_channel:
            await target_channel.delete()
            await ctx.reply(f'The channel {target_channel.name} has been deleted.')
        else:
            # If no channel is mentioned, delete the current channel
            await ctx.channel.delete()
            await ctx.reply(f'The channel {ctx.channel.name} has been deleted.')

    @commands.command(name='perm')
    async def give_permissions(self, ctx, user: discord.Member):
        overwrites = ctx.channel.overwrites_for(user)
        overwrites.read_messages = True
        overwrites.send_messages = True
        await ctx.channel.set_permissions(user, overwrite=overwrites)
        await ctx.reply(f'Read and write permissions granted to {user.mention}.')

    @commands.command(name='dperm')
    async def remove_permissions(self, ctx, user: discord.Member):
        overwrites = ctx.channel.overwrites_for(user)
        overwrites.read_messages = False
        overwrites.send_messages = False
        await ctx.channel.set_permissions(user, overwrite=overwrites)
        await ctx.reply(f'Read and write permissions removed for {user.mention}.')


            
    @commands.command(name="deleteinvites")
    @commands.has_permissions(manage_guild=True)  # Require 'Manage Server' permission
    async def delete_invites(self, ctx):
        """Deletes all invite links in the current server."""
        invites = await ctx.guild.invites()
        if not invites:
            await ctx.reply("No invites found.")
            return

        count = 0
        for invite in invites:
            await invite.delete()
            count += 1

        await ctx.reply(f"Deleted {count} invite(s).")
            
        
    @commands.command(name='banda')
    async def userinfo(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        # Fetch the user's full profile to get the banner
        user = await self.bot.fetch_user(member.id)
        banner_url = user.banner.url if user.banner else None

        roles = [role for role in member.roles if role != ctx.guild.default_role]
        role_string = ', '.join([role.mention for role in roles]) if roles else 'None'

        # Get the color of the highest role
        highest_role_color = member.top_role.color if roles else discord.Color.default()

        embed = discord.Embed(color=highest_role_color)
        embed.set_author(name=str(member), icon_url=member.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name='Server Joined', value=member.joined_at.strftime('%a, %b %d, %Y %I:%M %p'), inline=True)
        embed.add_field(name='Registered', value=member.created_at.strftime('%a, %b %d, %Y %I:%M %p'), inline=True)
        embed.add_field(name='Booster Since', value=member.premium_since.strftime('%a, %b %d, %Y %I:%M %p') if member.premium_since else 'Not boosting', inline=True)
        embed.add_field(name='Roles', value=role_string, inline=False)

        permissions = [perm[0].replace('_', ' ').title() for perm in member.guild_permissions if perm[1]]
        embed.add_field(name='Key Permissions', value=', '.join(permissions) if permissions else 'None', inline=False)

        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(text=f'ID: {member.id}')
        embed.timestamp = datetime.utcnow()

        await ctx.reply(embed=embed)





async def setup(bot):
    await bot.add_cog(Management(bot))