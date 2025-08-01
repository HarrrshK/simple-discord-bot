import discord
from discord.ext import commands
import json

class ChangeRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.permissions_backup = {}

    def save_permissions(self, guild_id, role_id, channel_id, perms):
        if guild_id not in self.permissions_backup:
            self.permissions_backup[guild_id] = {}
        if role_id not in self.permissions_backup[guild_id]:
            self.permissions_backup[guild_id][role_id] = {}
        self.permissions_backup[guild_id][role_id][channel_id] = perms

    def get_saved_permissions(self, guild_id, role_id, channel_id):
        return self.permissions_backup.get(guild_id, {}).get(role_id, {}).get(channel_id, None)

    @commands.command(name="rperms", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def reset_perms(self, ctx, *roles: discord.Role):
        guild = ctx.guild
        
        for role in roles:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    current_perms = channel.overwrites_for(role)
                    self.save_permissions(guild.id, role.id, channel.id, current_perms)
                    await channel.set_permissions(role, overwrite=discord.PermissionOverwrite())

        await ctx.send(f"Permissions for the mentioned roles are ggs")

    @commands.command(name="reperms", pass_context=True)
    @commands.has_permissions(administrator=True)
    async def restore_perms(self, ctx, *roles: discord.Role):
        guild = ctx.guild

        for role in roles:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    saved_perms = self.get_saved_permissions(guild.id, role.id, channel.id)
                    if saved_perms is not None:
                        await channel.set_permissions(role, overwrite=saved_perms)
        
        await ctx.send(f"epermissions for the mentioned roles are back bhenchod")


async def setup(bot):
    await bot.add_cog(ChangeRoles(bot))