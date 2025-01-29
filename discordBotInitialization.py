from discord.ext import commands

def start_discord_bot(agent):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())
    
    # Load Discord bot with API key
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    # Load commands into bot
    bot.add_cog(ParadoxDiscordBot(bot, agent, int(DISCORD_ADMIN_CHANNEL_ID)))

    # Start bot
    bot.run(DISCORD_BOT_TOKEN)
