import os
import tweepy
from dotenv import load_dotenv

# Load API keys
load_dotenv()
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_ADMIN_HANDLE = os.getenv("TWITTER_ADMIN_HANDLE")

class ParadoxTwitterBot:
    def __init__(self, agent):
        self.agent = agent

        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        self.api = tweepy.API(auth)
        self.stream_listener = TwitterStreamListener(self)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)

    def process_command(self, sender, message):
        """Processes commands sent via Twitter DM from the admin."""
        if sender != TWITTER_ADMIN_HANDLE:
            return "Unauthorized: You are not the designated admin."

        command_parts = message.split()
        command = command_parts[0].lower()

        if command == "trade":
            if len(command_parts) < 4:
                return "Usage: trade <from_token> <to_token> <amount>"
            return self.agent.trade(command_parts[1], command_parts[2], float(command_parts[3]))

        if command == "track_wallet":
            if len(command_parts) < 2:
                return "Usage: track_wallet <wallet_address>"
            return self.agent.track_wallet(command_parts[1])

        if command == "post":
            msg = " ".join(command_parts[1:])
            return self.agent.send_post("Twitter", msg)

        if command == "report":
            return self.agent.generate_report()

        return "Invalid command."

    def run(self):
        """Starts listening for direct messages from the admin."""
        self.stream.filter(track=[f"@{TWITTER_ADMIN_HANDLE}"], is_async=True)

class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def on_direct_message(self, status):
        """Handles incoming direct messages."""
        sender = status.direct_message["sender_screen_name"]
        message = status.direct_message["text"]
        response = self.bot.process_command(sender, message)
        self.bot.api.send_direct_message(sender, response)
