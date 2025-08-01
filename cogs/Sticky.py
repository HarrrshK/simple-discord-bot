import discord
from discord.ext import commands
import sqlite3

class Sticky(commands.Cog):
    """
    This category has the commands which are sticky!!!!
    """

    def __init__(self, bot):
        self.bot = bot

        # Establish an SQLite database connection
        self.conn = sqlite3.connect("botdata_luffy.db")
        self.c = self.conn.cursor()

        # Create tables if they don't exist
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS sticky_kick (
                        guild_id INTEGER,
                        user_id INTEGER,
                        UNIQUE(guild_id, user_id)
                    )"""
        )
        self.conn.commit()

        self.c.execute(
            """CREATE TABLE IF NOT EXISTS sticky_delete_msg (
                        guild_id INTEGER,
                        user_id INTEGER,
                        UNIQUE(guild_id, user_id)
                    )"""
        )
        self.conn.commit()

        self.c.execute(
            """CREATE TABLE IF NOT EXISTS sticky_usernames (
                        guild_id INTEGER,
                        user_id INTEGER,
                        sticky_nickname TEXT,
                        UNIQUE(guild_id, user_id)
                    )"""
        )
        self.conn.commit()

    @commands.command(name="stickykick")
    @commands.has_permissions(administrator=True)
    async def set_sticky_kick(self, ctx, user: discord.User):
        """Set a user to be kicked upon rejoining."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "INSERT OR IGNORE INTO sticky_kick (guild_id, user_id) VALUES (?, ?)",
            (guild_id, user_id),
        )
        self.conn.commit()

        await ctx.guild.kick(user, reason="Sticky kick set by command")
        await ctx.reply(f"{user.mention} has been set for sticky kick.")

    @commands.command(name="removestickykick")
    @commands.has_permissions(administrator=True)
    async def remove_sticky_kick(self, ctx, user: discord.User):
        """Remove a user from the sticky kick list."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "DELETE FROM sticky_kick WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        self.conn.commit()

        await ctx.reply(f"{user.mention} has been removed from the sticky kick list.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        user_id = member.id

        self.c.execute(
            "SELECT 1 FROM sticky_kick WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        result = self.c.fetchone()

        if result:
            await member.kick(reason="Sticky kick enforced on join")

    @commands.command(name="stickydeletemsg")
    @commands.has_permissions(administrator=True)
    async def set_sticky_delete_msg(self, ctx, user: discord.User):
        """Enable sticky message deletion for the specified user."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "INSERT OR IGNORE INTO sticky_delete_msg (guild_id, user_id) VALUES (?, ?)",
            (guild_id, user_id),
        )
        self.conn.commit()

        await ctx.reply(f"Sticky message deletion enabled for {user.mention}.")

    @commands.command(name="removestickydeletemsg")
    @commands.has_permissions(administrator=True)
    async def remove_sticky_delete_msg(self, ctx, user: discord.User):
        """Disable sticky message deletion for the specified user."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "DELETE FROM sticky_delete_msg WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        self.conn.commit()

        await ctx.reply(f"Sticky message deletion disabled for {user.mention}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore messages from bots

        guild_id = message.guild.id
        user_id = message.author.id

        self.c.execute(
            "SELECT 1 FROM sticky_delete_msg WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        result = self.c.fetchone()

        if result:
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass  # Message may have already been deleted

    @commands.command(name="stickyusername")
    @commands.has_permissions(administrator=True)
    async def set_sticky_nickname(self, ctx, user: discord.User, *, nickname: str):
        """Set a sticky username for a user."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "INSERT OR REPLACE INTO sticky_usernames (guild_id, user_id, sticky_nickname) VALUES (?, ?, ?)",
            (guild_id, user_id, nickname),
        )
        self.conn.commit()

        # Set the nickname immediately
        guild_member = ctx.guild.get_member(user_id)
        if guild_member:
            await guild_member.edit(nick=nickname)

        await ctx.reply(f"Sticky nickname set for {user.mention}: {nickname}")

    @commands.command(name="removestickyusername")
    @commands.has_permissions(administrator=True)
    async def remove_sticky_nickname(self, ctx, user: discord.User):
        """Remove a sticky username for a user."""
        guild_id = ctx.guild.id
        user_id = user.id

        self.c.execute(
            "DELETE FROM sticky_usernames WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        self.conn.commit()

        await ctx.reply(f"Sticky nickname removed for {user.mention}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            guild_id = before.guild.id
            user_id = before.id

            self.c.execute(
                "SELECT sticky_nickname FROM sticky_usernames WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            result = self.c.fetchone()

            if result:
                sticky_nickname = result[0]
                if after.nick != sticky_nickname:
                    await after.edit(nick=sticky_nickname)

async def setup(bot):
    await bot.add_cog(Sticky(bot))
