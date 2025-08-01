import discord
from discord.ext import commands
from pretty_help import PrettyHelp
import random



def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

class FunCog(commands.Cog):
    """
    This category holds the fun related bot commands!!!!
    """

    def __init__(self, bot):
        self.bot = bot
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun is loaded")

    @commands.command()
    async def ship(self, ctx, user1: discord.Member = None, user2: discord.Member = None):
       
        if not user1 and not user2:
            online_members = [m for m in ctx.guild.members if m.status == discord.Status.online and not m.bot]
            if len(online_members) < 2:
                await ctx.reply("Not enough online members to ship.")
                return
            user1, user2 = random.sample(online_members, 2)

        elif not user2:
            user2 = ctx.author

        love_percentage = random.randint(0, 100)


        embed = discord.Embed(
            title="Shipping Result",
            description=f"{user1.display_name} 💕 {user2.display_name}\nCompatibility: {love_percentage}%",
            color=discord.Color.purple()
        )
 
        embed.set_thumbnail(url=user1.display_avatar.url)
    
        embed.set_image(url=user2.display_avatar.url)

      
        await ctx.reply(embed=embed)

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            # Split the dice expression to get number of dice and type of dice
            num_dice, dice_type = map(int, dice.split('d'))
        except Exception as e:
            await ctx.send("Invalid input format. Please use {prefix}roll {no of dice}d{dice type}")
            return

        # Roll the dice
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        total = sum(rolls)

        # Determine embed color based on the total result
        if total == 1:
            color = discord.Color.red()
        elif total == num_dice * dice_type:
            color = discord.Color.green()
        else:
            color = discord.Color.blue()

        # Create embed
        embed = discord.Embed(title="Dice Roll", description=f"Total: {total}\nRolls: {' '.join(map(str, rolls))}", color=color)
        await ctx.send(embed=embed)

    def display_board(self):
        return f"{'|'.join(self.board[:3])}\n{'-+-+-'}\n{'|'.join(self.board[3:6])}\n{'-+-+-'}\n{'|'.join(self.board[6:])}"

    @commands.command()
    async def startgame(self, ctx):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        await ctx.send("Tic Tac Toe game started! X goes first.\n" + self.display_board())

    @commands.command()
    async def makemove(self, ctx, position: int):
        if self.board[position - 1] == ' ':
            self.board[position - 1] = self.current_player
            await ctx.send(self.display_board())
            if self.check_win():
                await ctx.send(f"{self.current_player} wins!")
                self.board = [' ' for _ in range(9)]
                return
            elif self.check_draw():
                await ctx.send("It's a draw!")
                self.board = [' ' for _ in range(9)]
                return
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            await ctx.send(f"It's {self.current_player}'s turn.")
        else:
            await ctx.send("That position is already taken.")

    def check_win(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != ' ':
                return True
        return False

    def check_draw(self):
        return ' ' not in self.board



async def setup(bot):
    await bot.add_cog(FunCog(bot))