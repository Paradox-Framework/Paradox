from discord.ext import commands

def start_discord_bot(agent):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())
    
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot.add_cog(ParadoxDiscordBot(bot, agent, int(DISCORD_ADMIN_CHANNEL_ID)))

    bot.run(DISCORD_BOT_TOKEN)
