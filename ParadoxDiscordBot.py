import discord
from discord.ext import commands

class ParadoxDiscordBot(commands.Cog):
    def __init__(self, bot, agent, admin_channel_id):
        self.bot = bot
        self.agent = agent
        self.admin_channel_id = admin_channel_id  # Admin-only command channel

    @commands.command(name="set_admin")
    async def set_admin(self, ctx, new_admin: discord.Member):
        """Assigns a new admin to manage the agent (Admin Only)."""
        if ctx.channel.id != self.admin_channel_id:
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
        if ctx.channel.id != self.admin_channel_id:
            return await ctx.send("This command can only be used in the admin channel.")
        self.agent.send_post(ctx.channel.id, message)
        await ctx.send("Message posted.")

    @commands.command(name="report")
    async def post_report(self, ctx):
        """Posts a summary of recent market/trading activity."""
        if ctx.channel.id != self.admin_channel_id:
            return await ctx.send("This command can only be used in the admin channel.")
        report = self.agent.generate_report()
        await ctx.send(report)

def setup(bot, agent, admin_channel_id):
    bot.add_cog(ParadoxDiscordBot(bot, agent, admin_channel_id))
