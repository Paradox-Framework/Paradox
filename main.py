#PARADOX AI : 2/21/2025

import solana.rpc.api
from solders.keypair import Keypair
from discord.ext import commands
from discord import app_commands
from typing import Final
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import discord, requests, base64, base58, asyncio, time, tweepy, json, os
import tokenomics, trading, wallettracking



# Loading Details From Config File #
#------------------------------------------------------------------------------------------------------------#

CONFIG_FILE = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file '{CONFIG_FILE}' not found.")

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

SECRET_KEY = config["SECRET_KEY"]
PRIVATE_RPC_ENDPOINT = config["PRIVATE_RPC_ENDPOINT"]
ASSOCIATED_TOKEN_CA = config["ASSOCIATED_TOKEN_CA"]
TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]
CHAT_ID = config["CHAT_ID"]
DISCORD_TOKEN = config["DISCORD_TOKEN"]
SERVER_ID = config["SERVER_ID"]
TWITTER_API_KEY = config["TWITTER_API_KEY"]
TWITTER_API_SECRET = config["TWITTER_API_SECRET"]
TWITTER_BEARER_TOKEN = config["TWITTER_BEARER_TOKEN"]
ACCESS_TOKEN = config["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = config["ACCESS_TOKEN_SECRET"]
SOLSCAN_API_KEY = config["SOLSCAN_API_KEY"]


# CLIENT AND TRADING SETUP #
#------------------------------------------------------------------------------------------------------------#

sol_client = solana.rpc.api.Client(PRIVATE_RPC_ENDPOINT)

keypair = Keypair.from_bytes(base58.b58decode(SECRET_KEY))
print(f'Account {keypair.pubkey()} loaded...')

if sol_client.get_version():
    print('Successfully connected to Solana Blockchain\nTrading Set Up Complete.')
else:
    print('Failed to connect to Solana. (FIX BEFORE ATTEMPTING TO TRADE)')


# HELPER FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#

ADMIN_FILE = "admins.json"
admins = set()

MAX_TWEET_LENGTH = 280

def split_tweet(message):
    messages = []
    while len(message) > MAX_TWEET_LENGTH:
        split_index = message[:MAX_TWEET_LENGTH].rfind(" ")
        if split_index == -1:
            split_index = MAX_TWEET_LENGTH
        messages.append(message[:split_index])
        message = message[split_index:].strip()
    messages.append(message)
    return messages


def load_admins():
    global admins
    try:
        with open(ADMIN_FILE, "r") as f:
            data = json.load(f)
            admins = set(data.get("admins", []))
    except (FileNotFoundError, json.JSONDecodeError):
        admins = set()

def save_admins():
    with open(ADMIN_FILE, "w") as f:
        json.dump({"admins": list(admins)}, f, indent=4)

def is_admin(user_id: int) -> bool:
    return user_id in admins

def admin_only():
    async def predicate(interaction: discord.Interaction):
        if is_admin(interaction.user.id):
            return True
        await interaction.response.send_message("❌ This command requires admin privileges.", ephemeral=True)
        return False
    return app_commands.check(predicate)



# CONTROLLER AND RESPONDER BOTS #
#------------------------------------------------------------------------------------------------------------#

telegram_bot = Bot(token=TELEGRAM_TOKEN)
twitter_client = tweepy.Client(TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
tapi = tweepy.API(auth)

autotrade_tasks = {}
tracking_tasks = {}
buywhen_tasks = {}
sellwhen_tasks = {}

class Client(commands.Bot):

    async def on_ready(self):

        print(f'{self.user} is online')

        load_admins()
        print(f'Loaded {len(admins)} admins from storage.')

        try:
            guild = discord.Object(id=1324584515682697318)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to server {guild.id}')
        except Exception as e:
            print(f'Error: {e}')

    async def on_message(self, message):

        if message.author == self.user:
            return

        print(f'{message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)
GUILD_ID = discord.Object(id=SERVER_ID)


# BOT HELPER FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#


@client.tree.command(name='stopall', description='Stops all active trading and tracking sessions.', guild=GUILD_ID)
async def stopall(interaction: discord.Interaction):
    user_id = interaction.user.id
    stopped_sessions = []

    if user_id in autotrade_tasks:
        for ca in list(autotrade_tasks[user_id].keys()):
            autotrade_tasks[user_id][ca].cancel()
            stopped_sessions.append(f"Autotrade `{ca}`")
        del autotrade_tasks[user_id]

    if user_id in buywhen_tasks:
        for ca in list(buywhen_tasks[user_id].keys()):
            buywhen_tasks[user_id][ca].cancel()
            stopped_sessions.append(f"Buywhen `{ca}`")
        del buywhen_tasks[user_id]

    if user_id in sellwhen_tasks:
        for ca in list(sellwhen_tasks[user_id].keys()):
            sellwhen_tasks[user_id][ca].cancel()
            stopped_sessions.append(f"Sellwhen `{ca}`")
        del sellwhen_tasks[user_id]

    if user_id in tracking_tasks:
        for walletaddress in list(tracking_tasks[user_id].keys()):
            tracking_tasks[user_id][walletaddress].cancel()
            stopped_sessions.append(f"Tracking `{walletaddress}`")
        del tracking_tasks[user_id]

    if stopped_sessions:
        stopped_message = "**Stopped the following sessions:**\n" + "\n".join(stopped_sessions)
    else:
        stopped_message = "No active sessions found."

    await interaction.response.send_message(stopped_message)


@client.tree.command(name='listactivity', description='Lists all active trading and tracking sessions.', guild=GUILD_ID)
async def listactivity(interaction: discord.Interaction):
    user_id = interaction.user.id
    active_sessions = []

    # List all `autotrade` sessions
    if user_id in autotrade_tasks and autotrade_tasks[user_id]:
        autotrades = "\n".join(f"- `{ca}`" for ca in autotrade_tasks[user_id].keys())
        active_sessions.append(f"**Autotrades:**\n{autotrades}")

    # List all `buywhen` sessions
    if user_id in buywhen_tasks and buywhen_tasks[user_id]:
        buywhens = "\n".join(f"- `{ca}`" for ca in buywhen_tasks[user_id].keys())
        active_sessions.append(f"**Buywhen Sessions:**\n{buywhens}")

    # List all `sellwhen` sessions
    if user_id in sellwhen_tasks and sellwhen_tasks[user_id]:
        sellwhens = "\n".join(f"- `{ca}`" for ca in sellwhen_tasks[user_id].keys())
        active_sessions.append(f"**Sellwhen Sessions:**\n{sellwhens}")

    # List all `track` sessions
    if user_id in tracking_tasks and tracking_tasks[user_id]:
        tracks = "\n".join(f"- `{walletaddress}`" for walletaddress in tracking_tasks[user_id].keys())
        active_sessions.append(f"**Tracking Sessions:**\n{tracks}")

    # Send response
    if active_sessions:
        response_message = "\n\n".join(active_sessions)
    else:
        response_message = "You have no active sessions."

    await interaction.response.send_message(response_message)


# ADMIN FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#


@client.tree.command(name='setadmin', description='Adds a new admin.', guild=GUILD_ID)
@admin_only()
async def setadmin(interaction: discord.Interaction, user: discord.User):
    """Adds a user as an admin."""
    if user.id in admins:
        await interaction.response.send_message(f"⚠️ {user.mention} is already an admin.")
        return

    admins.add(user.id)
    save_admins()
    await interaction.response.send_message(f"✅ {user.mention} has been added as an admin.")


@client.tree.command(name='listadmins', description='Lists all current admins.', guild=GUILD_ID)
@admin_only()
async def listadmins(interaction: discord.Interaction):
    """Lists all admins."""
    if not admins:
        await interaction.response.send_message("⚠️ No admins found.")
        return

    admin_list = "\n".join(f"- <@{admin_id}>" for admin_id in admins)
    await interaction.response.send_message(f"**Current Admins:**\n{admin_list}")


@client.tree.command(name='removeadmin', description='Removes an admin.', guild=GUILD_ID)
@admin_only()
async def removeadmin(interaction: discord.Interaction, user: discord.User):
    """Removes an admin."""
    if user.id not in admins:
        await interaction.response.send_message("⚠️ That user is not an admin.")
        return

    if len(admins) == 1 and user.id in admins:
        await interaction.response.send_message("❌ Cannot remove the last admin!")
        return

    admins.remove(user.id)
    save_admins()
    await interaction.response.send_message(f"✅ {user.mention} has been removed from admins.")


# TRADING FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#

@client.tree.command(name='buy', description='Purchases a coin', guild=GUILD_ID)
@admin_only()
async def buy(interaction: discord.Interaction, ca: str, amount: float, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    amount_in_lamports = (int)(amount * 1_000_000_000)

    details = trading.buy(ca, amount_in_lamports, keypair=keypair, client=sol_client)
    symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
    name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)


    if moredetails:
        message = (f'Purchased: {symbol}: {name}\n'
                   f'Amount: {amount} SOL\n'
                   f'Account Used: {keypair.pubkey()}\n'
                   f'Transaction Details: {details}')
    else:
        message = (f'Purchased: {symbol}: {name}\n'
                   f'Amount: {amount} SOL\n'
                   f'Account Used: {keypair.pubkey()}')

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='sell', description='Sells a coin', guild=GUILD_ID)
@admin_only()
async def sell(interaction: discord.Interaction, ca: str, amount: float, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    amount_in_lamports = (int)(amount * 1_000_000_000)

    details = trading.sell(ca, amount_in_lamports, keypair=keypair, client=sol_client)
    symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
    name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)


    if moredetails:
        message = (f'Sold: {symbol}: {name}\n'
                   f'Amount: {amount} SOL\n'
                   f'Account Used: {keypair.pubkey()}\n'
                   f'Transaction Details: {details}')
    else:
        message = (f'Sold: {symbol}: {name}\n'
                   f'Amount: {amount} SOL\n'
                   f'Account Used: {keypair.pubkey()}')

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='buywhen', description='Purchases a coin at a certain price or market cap', guild=GUILD_ID)
@admin_only()
async def buywhen(interaction: discord.Interaction, ca: str, amount: float, determinant: str, limit: float, totaltime_in_minutes: int = 60, reqs_per_minute: int = 1, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    user_id = interaction.user.id

    if user_id in buywhen_tasks and ca in buywhen_tasks[user_id]:
        await interaction.followup.send(f"Session `{ca}` already exists. Choose a different coin.")
        return

    async def run_buywhen():
        symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
        name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)

        if determinant == 'price':

            await interaction.followup.send(f'Watching Price of {symbol}: {name}...')

            for i in range(totaltime_in_minutes * reqs_per_minute):

                currentPrice = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
                print(f'Comparing current price: {currentPrice} to limit: {limit}.')
                if currentPrice <= limit:

                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.buy(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                await asyncio.sleep(60 / reqs_per_minute)

        elif determinant == 'mcap':

            await interaction.followup.send(f'Watching Market Cap of {symbol}: {name}...')

            for i in range(totaltime_in_minutes * reqs_per_minute):

                currentMcap = tokenomics.getMarketCap(ca, SOLSCAN_API_KEY)
                print(f'Comparing current market cap: {currentMcap} to limit: {limit}.')
                if currentMcap <= limit:
                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.buy(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                await asyncio.sleep(60 / reqs_per_minute)

        else:
            await interaction.followup.send(f'Type either "price" or "mcap" in determinant field.')

        if user_id in buywhen_tasks and ca in buywhen_tasks[user_id]:
            del buywhen_tasks[user_id][ca]
            if not buywhen_tasks[user_id]:
                del buywhen_tasks[user_id]

    if user_id not in buywhen_tasks:
        buywhen_tasks[user_id] = {}

    task = asyncio.create_task(run_buywhen())
    buywhen_tasks[user_id][ca] = task


@client.tree.command(name='stopbuywhen', description='Stops a specific buywhen session', guild=GUILD_ID)
@admin_only()
async def stopbuywhen(interaction: discord.Interaction, ca: str):
    user_id = interaction.user.id

    if user_id in buywhen_tasks and ca in buywhen_tasks[user_id]:
        buywhen_tasks[user_id][ca].cancel()
        del buywhen_tasks[user_id][ca]

        if not buywhen_tasks[user_id]:
            del buywhen_tasks[user_id]

        await interaction.response.send_message(f"Buywhen `{ca}` stopped successfully!")
    else:
        await interaction.response.send_message(f"No active buywhen session found with ID `{ca}`.")


@client.tree.command(name='listbuywhens', description='Lists all active buywhen sessions', guild=GUILD_ID)
@admin_only()
async def listbuywhens(interaction: discord.Interaction):
    user_id = interaction.user.id

    if user_id in buywhen_tasks and buywhen_tasks[user_id]:
        active_sessions = "\n".join(f"- `{ca}`" for ca in buywhen_tasks[user_id].keys())
        await interaction.response.send_message(f"**Your Active Buywhen Sessions:**\n{active_sessions}")
    else:
        await interaction.response.send_message("You have no active buywhen sessions.")



@client.tree.command(name='sellwhen', description='Sells a coin at a certain price or market cap', guild=GUILD_ID)
@admin_only()
async def sellwhen(interaction: discord.Interaction, ca: str, amount: float, determinant: str, limit: float, totaltime_in_minutes: int = 60, reqs_per_minute: int = 1, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    user_id = interaction.user.id

    if user_id in sellwhen_tasks and ca in sellwhen_tasks[user_id]:
        await interaction.followup.send(f"Session `{ca}` already exists. Choose a different ID.")
        return

    async def run_sellwhen():

        symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
        name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)

        if determinant == 'price':

            await interaction.followup.send(f'Watching Price of {symbol}: {name}...')

            for i in range(totaltime_in_minutes * reqs_per_minute):

                currentPrice = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
                print(f'Comparing current price: {currentPrice} to limit: {limit}.')
                if currentPrice >= limit:

                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.sell(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Sold: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Sold: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                await asyncio.sleep(60 / reqs_per_minute)

        elif determinant == 'mcap':

            await interaction.followup.send(f'Watching Market Cap of {symbol}: {name}...')

            for i in range(totaltime_in_minutes * reqs_per_minute):

                currentMcap = tokenomics.getMarketCap(ca, SOLSCAN_API_KEY)
                print(f'Comparing current market cap: {currentMcap} to limit: {limit}.')
                if currentMcap >= limit:
                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.sell(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Sold: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Sold: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                await asyncio.sleep(60 / reqs_per_minute)

        else:
            await interaction.followup.send(f'Type either "price" or "mcap" in determinant field.')

        if user_id in sellwhen_tasks and ca in sellwhen_tasks[user_id]:
            del sellwhen_tasks[user_id][ca]
            if not sellwhen_tasks[user_id]:  # Remove user if no more sessions
                del sellwhen_tasks[user_id]

    if user_id not in sellwhen_tasks:
        sellwhen_tasks[user_id] = {}

    task = asyncio.create_task(run_sellwhen())
    sellwhen_tasks[user_id][ca] = task


@client.tree.command(name='stopsellwhen', description='Stops a specific sellwhen session', guild=GUILD_ID)
@admin_only()
async def stopsellwhen(interaction: discord.Interaction, ca: str):
    user_id = interaction.user.id

    if user_id in sellwhen_tasks and ca in sellwhen_tasks[user_id]:
        sellwhen_tasks[user_id][ca].cancel()  # Cancel task
        del sellwhen_tasks[user_id][ca]  # Remove from dictionary

        if not sellwhen_tasks[user_id]:  # If no trades left, remove user entry
            del sellwhen_tasks[user_id]

        await interaction.response.send_message(f"Sellwhen `{ca}` stopped successfully!")
    else:
        await interaction.response.send_message(f"No active sellwhen session found with ID `{ca}`.")


@client.tree.command(name='listsellwhens', description='Lists all active sellwhen sessions', guild=GUILD_ID)
@admin_only()
async def listsellwhens(interaction: discord.Interaction):
    user_id = interaction.user.id

    if user_id in sellwhen_tasks and sellwhen_tasks[user_id]:
        active_sessions = "\n".join(f"- `{ca}`" for ca in sellwhen_tasks[user_id].keys())
        await interaction.response.send_message(f"**Your Active Sellwhen Sessions:**\n{active_sessions}")
    else:
        await interaction.response.send_message("You have no active sellwhen sessions.")


@client.tree.command(name='autotrade', description='Purchases or sells a coin when it gains or loses a certain percentage', guild=GUILD_ID)
@admin_only()
async def autotrade(interaction: discord.Interaction, ca: str, amount: float, personality: str, gain_percent_change: float = 100.0, loss_percent_change: float = 50.0, totaltime_in_minutes: int = 60, reqs_per_minute: int = 1, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    user_id = interaction.user.id

    if user_id in autotrade_tasks and ca in autotrade_tasks[user_id]:
        await interaction.followup.send(f"Session `{ca}` already exists. Choose a different coin.")
        return

    async def run_autotrade(ca=ca, amount=amount, personality=personality, gain_percent_change=gain_percent_change, loss_percent_change=loss_percent_change, totaltime_in_minutes=totaltime_in_minutes, reqs_per_minute=reqs_per_minute, moredetails=moredetails, platform=platform):
        symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
        name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)
        startPrice = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
        personality = personality.lower()

        if personality in {'custom', 'scalper', 'safe', 'conservative', 'aggressive', 'degen'}:

            if personality == 'scalper':
                targetLoss = startPrice - (startPrice * 0.03)
                targetGain = startPrice + (startPrice * 0.05)

            elif personality == 'safe':
                targetLoss = startPrice - (startPrice * 0.15)
                targetGain = startPrice + (startPrice * 0.2)

            elif personality == 'conservative':
                targetLoss = startPrice - (startPrice * 0.2)
                targetGain = startPrice + (startPrice * 0.4)

            elif personality == 'aggressive':
                targetLoss = startPrice - (startPrice * 0.25)
                targetGain = startPrice + (startPrice * 0.5)

            elif personality == 'degen':
                targetLoss = startPrice - (startPrice * 0.7)
                targetGain = startPrice + (startPrice * 2.5)

            else:
                gainPercentChange = gain_percent_change / 100
                lossPercentChange = loss_percent_change / 100
                targetLoss = startPrice - (startPrice * lossPercentChange)
                targetGain = startPrice + (startPrice * gainPercentChange)


            await interaction.followup.send(f'Watching Price of {symbol}: {name}...')


            for i in range(totaltime_in_minutes * reqs_per_minute):

                currentPrice = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
                print(f'Current price: {currentPrice} Price Target to Buy: {targetLoss}.')
                if currentPrice <= targetLoss:

                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.buy(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                print(f'Current price: {currentPrice} Price Target to Sell: {targetGain}.')
                if currentPrice >= targetGain:
                    amount_in_lamports = (int)(amount * 1_000_000_000)

                    details = trading.buy(ca, amount_in_lamports, keypair=keypair, client=sol_client)

                    if moredetails:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}\n'
                                   f'Transaction Details: {details}')
                    else:
                        message = (f'Purchased: {symbol}: {name}\n'
                                   f'Amount: {amount} SOL\n'
                                   f'Account Used: {keypair.pubkey()}')

                    try:
                        if platform == 'telegram':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'twitter':
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on {platform}')
                            await interaction.followup.send(f'Sent: "{message}" on {platform}')
                        elif platform == 'all':
                            await telegram_bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode=ParseMode.HTML
                            )
                            tweets = split_tweet(message)
                            for tweet in tweets:
                                twitter_client.create_tweet(text=tweet)
                            print(f'Sent "{message}" on all platforms')
                            await interaction.followup.send(f'Sent: "{message}" on all platforms')
                        else:
                            print(f'{message}')
                            await interaction.followup.send(f'{message}')
                    except TelegramError as e:
                        await interaction.followup.send(f"Failed to send message to Telegram: {e}")

                    break

                await asyncio.sleep(60 / reqs_per_minute)
        else:
            await interaction.followup.send(f'Invalid personality: {personality}.')

        if user_id in autotrade_tasks and ca in autotrade_tasks[user_id]:
            del autotrade_tasks[user_id][ca]
            if not autotrade_tasks[user_id]:  # Remove user if no more sessions
                del autotrade_tasks[user_id]

    if user_id not in autotrade_tasks:
        autotrade_tasks[user_id] = {}

    task = asyncio.create_task(run_autotrade())
    autotrade_tasks[user_id][ca] = task

    await interaction.followup.send(f"Autotrade started.")


@client.tree.command(name='stopautotrade', description='Stops a specific autotrade session', guild=GUILD_ID)
@admin_only()
async def stopautotrade(interaction: discord.Interaction, ca: str):
    user_id = interaction.user.id

    if user_id in autotrade_tasks and ca in autotrade_tasks[user_id]:
        autotrade_tasks[user_id][ca].cancel()
        del autotrade_tasks[user_id][ca]

        if not autotrade_tasks[user_id]:
            del autotrade_tasks[user_id]

        await interaction.response.send_message(f"Autotrade `{ca}` stopped successfully!")
    else:
        await interaction.response.send_message(f"No active autotrade session found with ID `{ca}`.")


@client.tree.command(name='listautotrade', description='Lists all active autotrade sessions', guild=GUILD_ID)
@admin_only()
async def listautotrade(interaction: discord.Interaction):
    user_id = interaction.user.id

    if user_id in autotrade_tasks and autotrade_tasks[user_id]:
        active_sessions = "\n".join(f"- `{ca}`" for ca in autotrade_tasks[user_id].keys())
        await interaction.response.send_message(f"**Your Active Autotrade Sessions:**\n{active_sessions}")
    else:
        await interaction.response.send_message("You have no active autotrade sessions.")


# WALLET TRACKING FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#


@client.tree.command(name='track', description='Tracks a wallet address\'s transactions. Returns a transaction hash.', guild=GUILD_ID)
@admin_only()
async def track(interaction: discord.Interaction, walletaddress: str, totaltime_in_minutes: int = 60, reqs_per_minute: int = 1, moredetails: bool = False, platform: str = 'discord'):

    await interaction.response.defer()

    user_id = interaction.user.id

    if user_id in tracking_tasks and walletaddress in tracking_tasks[user_id]:
        await interaction.followup.send(f"Session `{walletaddress}` already exists. Choose a different ID.")
        return

    async def run_tracking():
        print(f'Watching {walletaddress}...')
        await interaction.followup.send(f'Watching {walletaddress}...')

        last = wallettracking.get_latest_transaction(walletaddress, SOLSCAN_API_KEY)
        for i in range(totaltime_in_minutes * reqs_per_minute):

            current = wallettracking.get_latest_transaction(walletaddress, SOLSCAN_API_KEY)
            if current != None and current != last:

                data = current['data'][0]
                tx_hash = data['tx_hash']
                slot = data['slot']
                fee = data['fee']
                status = data['status']
                blocktime = data['block_time']
                signer = data["signer"]


                if moredetails:
                    message = (f'**{walletaddress}** made a transaction:\n'
                               f'**Transaction Hash**: {tx_hash}\n'
                               f'**Slot**: {slot}\n',
                               f'**Fee**: {fee}\n',
                               f'**Status**: {status}\n',
                               f'**Blocktime**: {blocktime}\n',
                               f'**Signer**: {signer}')
                else:
                    message = (f'**{walletaddress}** made a transaction:\n'
                               f'**Transaction Hash**: {tx_hash}')

                try:
                    if platform == 'telegram':
                        await telegram_bot.send_message(
                            chat_id=CHAT_ID,
                            text=message,
                            parse_mode=ParseMode.HTML
                        )
                        print(f'Sent "{message}" on {platform}')
                        await interaction.followup.send(f'Sent: "{message}" on {platform}')
                    elif platform == 'twitter':
                        tweets = split_tweet(message)
                        for tweet in tweets:
                            twitter_client.create_tweet(text=tweet)
                        print(f'Sent "{message}" on {platform}')
                        await interaction.followup.send(f'Sent: "{message}" on {platform}')
                    elif platform == 'all':
                        await telegram_bot.send_message(
                            chat_id=CHAT_ID,
                            text=message,
                            parse_mode=ParseMode.HTML
                        )
                        tweets = split_tweet(message)
                        for tweet in tweets:
                            twitter_client.create_tweet(text=tweet)
                        print(f'Sent "{message}" on all platforms')
                        await interaction.followup.send(f'Sent: "{message}" on all platforms')
                    else:
                        print(f'{message}')
                        await interaction.followup.send(f'{message}')
                except TelegramError as e:
                    await interaction.followup.send(f"Failed to send message to Telegram: {e}")

            last = current
            await asyncio.sleep(60 / reqs_per_minute)

        if user_id in tracking_tasks and walletaddress in tracking_tasks[user_id]:
            del tracking_tasks[user_id][walletaddress]
            if not tracking_tasks[user_id]:
                del tracking_tasks[user_id]
        await interaction.followup.send(f'Stopped watching {walletaddress}...')

    if user_id not in tracking_tasks:
        tracking_tasks[user_id] = {}

    task = asyncio.create_task(run_tracking())
    tracking_tasks[user_id][walletaddress] = task


@client.tree.command(name='stoptrack', description='Stops a specific tracking session', guild=GUILD_ID)
@admin_only()
async def stoptrack(interaction: discord.Interaction, walletaddress: str):
    user_id = interaction.user.id

    if user_id in tracking_tasks and walletaddress in tracking_tasks[user_id]:
        tracking_tasks[user_id][walletaddress].cancel()  # Cancel task
        del tracking_tasks[user_id][walletaddress]  # Remove from dictionary

        if not tracking_tasks[user_id]:  # If no tracks left, remove user entry
            del tracking_tasks[user_id]

        await interaction.response.send_message(f"Tracking session `{walletaddress}` stopped successfully!")
    else:
        await interaction.response.send_message(f"No active tracking session found with ID `{walletaddress}`.")


@client.tree.command(name='listtracks', description='Lists all active tracking sessions', guild=GUILD_ID)
@admin_only()
async def listtracks(interaction: discord.Interaction):
    user_id = interaction.user.id

    if user_id in tracking_tasks and tracking_tasks[user_id]:
        active_sessions = "\n".join(f"- `{walletaddress}`" for walletaddress in tracking_tasks[user_id].keys())
        await interaction.response.send_message(f"**Your Active Tracking Sessions:**\n{active_sessions}")
    else:
        await interaction.response.send_message("You have no active tracking sessions.")


@client.tree.command(name='listtransactions', description='Tracks a wallet address\'s transactions. Returns a transaction hash.', guild=GUILD_ID)
@admin_only()
async def listtransactions(interaction: discord.Interaction, walletaddress: str, how_many: int = 10, platform: str = 'discord'):

    await interaction.response.defer()

    wallet = "3S5UsTni14WoWeG6Z3S2jzi5JQSoWteQJm3ubjGaQozo"
    transactions = wallettracking.get_solana_transactions(wallet, how_many)

    message = ''
    for tx in transactions:
        smallmessage = (f"**Transaction Signature**: {tx['signature']} \n **Slot**: {tx['slot']} \n **Block Time**: {tx.get('blockTime', 'N/A')}\n\n")
        message += smallmessage

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


# TOKENOMICS FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#

@client.tree.command(name='getcoindetails', description='Returns a coin\'s details on the desired platform', guild=GUILD_ID)
@admin_only()
async def getcoindetails(interaction: discord.Interaction, ca: str, platform: str = 'discord'):

    await interaction.response.defer()

    solUSD = tokenomics.getSolPrice(SOLSCAN_API_KEY)
    name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)
    symbol = tokenomics.getTokenSymbol(ca, SOLSCAN_API_KEY)
    price = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
    mcap = tokenomics.getMarketCap(ca, SOLSCAN_API_KEY)
    holdercount = tokenomics.getTokenHolderCount(ca, SOLSCAN_API_KEY)
    supply = tokenomics.getTokenSupply(ca, SOLSCAN_API_KEY)
    cointwitter = tokenomics.getTokenTwitter(ca, SOLSCAN_API_KEY)

    if 'Exit code -1' in cointwitter:
        message = (f'**Current Details of**: **{symbol}** - **{name}**\n'
                   f'**Price**: {price} SOL\n'
                   f'**Market Cap**: {mcap} SOL\n'
                   f'**Holder Count**: {holdercount}\n'
                   f'**Supply**: {supply}')
    else:
        message = (f'**Current Details of**: **{symbol}** - **{name}**\n'
                   f'**Price**: {price} SOL\n'
                   f'**Market Cap**: {mcap} SOL\n'
                   f'**Holder Count**: {holdercount}\n'
                   f'**Supply**: {supply}\n'
                   f'**Twitter**: {cointwitter}')

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='getprice', description='Returns a coin\'s price on the desired platform', guild=GUILD_ID)
@admin_only()
async def getprice(interaction: discord.Interaction, ca: str, platform: str = 'discord'):

    await interaction.response.defer()
    name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)
    price = tokenomics.getPrice(ca, SOLSCAN_API_KEY)
    message = f'Current Price of {name}: {price} SOL'

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='getmcap', description='Returns a coin\'s market cap on the desired platform', guild=GUILD_ID)
@admin_only()
async def getmcap(interaction: discord.Interaction, ca: str, platform: str = 'discord'):

    await interaction.response.defer()
    name = tokenomics.getTokenName(ca, SOLSCAN_API_KEY)
    mcap = tokenomics.getMarketCap(ca, SOLSCAN_API_KEY)
    message = f'Current Market Cap of {name}: {mcap} SOL'

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")




# ASSOCIATED TOKENOMICS FUNCTIONS #
#------------------------------------------------------------------------------------------------------------#


@client.tree.command(name='getmycoindetails', description='Returns the coin associated with this account\'s details on the desired platform', guild=GUILD_ID)
@admin_only()
async def getmycoindetails(interaction: discord.Interaction, platform: str = 'discord'):

    await interaction.response.defer()

    solUSD = tokenomics.getSolPrice(SOLSCAN_API_KEY)
    name = tokenomics.getTokenName(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    symbol = tokenomics.getTokenSymbol(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    price = tokenomics.getPrice(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    mcap = tokenomics.getMarketCap(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    holdercount = tokenomics.getTokenHolderCount(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    supply = tokenomics.getTokenSupply(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    cointwitter = tokenomics.getTokenTwitter(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)

    if 'Exit code -1' in cointwitter:
        message = (f'**Current Details of**: **{symbol}** - **{name}**\n'
                   f'**Price**: {price} SOL\n'
                   f'**Market Cap**: {mcap} SOL\n'
                   f'**Holder Count**: {holdercount}\n'
                   f'**Supply**: {supply}')
    else:
        message = (f'**Current Details of**: **{symbol}** - **{name}**\n'
                   f'**Price**: {price} SOL\n'
                   f'**Market Cap**: {mcap} SOL\n'
                   f'**Holder Count**: {holdercount}\n'
                   f'**Supply**: {supply}\n'
                   f'**Twitter**: {cointwitter}')

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='getmycoinprice', description='Returns the coin associated with this account\'s price on the desired platform', guild=GUILD_ID)
@admin_only()
async def getmycoinprice(interaction: discord.Interaction, platform: str = 'discord'):

    await interaction.response.defer()
    name = tokenomics.getTokenName(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    price = tokenomics.getPrice(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    message = f'Current Price of {name}: {price} SOL'

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")


@client.tree.command(name='getmycoinmcap', description='Returns the coin associated with this account\'s market cap on the desired platform', guild=GUILD_ID)
@admin_only()
async def getmycoinmcap(interaction: discord.Interaction, platform: str = 'discord'):

    await interaction.response.defer()
    name = tokenomics.getTokenName(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    mcap = tokenomics.getMarketCap(ASSOCIATED_TOKEN_CA, SOLSCAN_API_KEY)
    message = f'Current Market Cap of {name}: {mcap} SOL'

    try:
        if platform == 'telegram':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'twitter':
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on {platform}')
            await interaction.followup.send(f'Sent: "{message}" on {platform}')
        elif platform == 'all':
            await telegram_bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
            tweets = split_tweet(message)
            for tweet in tweets:
                twitter_client.create_tweet(text=tweet)
            print(f'Sent "{message}" on all platforms')
            await interaction.followup.send(f'Sent: "{message}" on all platforms')
        else:
            print(f'{message}')
            await interaction.followup.send(f'{message}')
    except TelegramError as e:
        await interaction.followup.send(f"Failed to send message to Telegram: {e}")



if __name__ == '__main__':
    # RUN BOT #
    client.run(DISCORD_TOKEN)

