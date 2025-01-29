import tweepy

class ParadoxTwitterBot:
    def __init__(self, api_key, api_secret, access_token, access_secret, agent, admin_user):
        self.agent = agent
        self.admin_user = admin_user  # Twitter handle of the admin user

        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth)
        self.stream_listener = TwitterStreamListener(self)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)

    def process_command(self, sender, message):
        """Processes commands sent via Twitter DM from the admin."""
        if sender != self.admin_user:
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
        self.stream.filter(track=[f"@{self.admin_user}"], is_async=True)

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
