import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load API keys
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_ADMIN_CHANNEL_ID = int(os.getenv("DISCORD_ADMIN_CHANNEL_ID"))

class ParadoxDiscordBot(commands.Cog):
    def __init__(self, bot, agent):
        self.bot = bot
        self.agent = agent

    @commands.command(name="set_admin")
    async def set_admin(self, ctx, new_admin: discord.Member):
        """Assigns a new admin to manage the agent (Admin Only)."""
        if ctx.channel.id != DISCORD_ADMIN_CHANNEL_ID:
            return await ctx.send("This command can only be used in the admin channel.")
        self.agent.set_admin(new_admin.id)
        await ctx.send(f"New admin set: {new_admin.mention}")

    @commands.command(name="trade")
    async def execute_trade(self, ctx, from_token, to_token, amount: float):
        """Executes a trade from one token to another."""
        response = self.agent.trade(from_token, to_token, amount)
        await ctx.send(response)

    @commands.command(name="track_wallet")
    async def track_wallet(self, ctx, wallet_address):
        """Monitors a specific wallet’s transactions."""
        response = self.agent.track_wallet(wallet_address)
        await ctx.send(response)

    @commands.command(name="post")
    async def post_message(self, ctx, *, message):
        """Manually sends a message from the bot (Admin Only)."""
        if ctx.channel.id != DISCORD_ADMIN_CHANNEL_ID:
            return await ctx.send("This command can only be used in the admin channel.")
        self.agent.send_post(ctx.channel.id, message)
        await ctx.send("Message posted.")

    @commands.command(name="report")
    async def post_report(self, ctx):
        """Posts a summary of recent market/trading activity."""
        if ctx.channel.id != DISCORD_ADMIN_CHANNEL_ID:
            return await ctx.send("This command can only be used in the admin channel.")
        report = self.agent.generate_report()
        await ctx.send(report)

def start_discord_bot(agent):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())
    bot.add_cog(ParadoxDiscordBot(bot, agent))
    bot.run(DISCORD_BOT_TOKEN)
