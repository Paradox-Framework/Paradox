import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load API keys
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = int(os.getenv("TELEGRAM_ADMIN_CHAT_ID"))

class ParadoxTelegramBot:
    def __init__(self, agent):
        self.agent = agent
        self.updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
        dp = self.updater.dispatcher

        dp.add_handler(CommandHandler("trade", self.execute_trade))
        dp.add_handler(CommandHandler("track_wallet", self.track_wallet))
        dp.add_handler(CommandHandler("post", self.post_message))
        dp.add_handler(CommandHandler("report", self.post_report))

    def execute_trade(self, update: Update, context: CallbackContext):
        """Executes a trade from one token to another."""
        if len(context.args) < 3:
            update.message.reply_text("Usage: /trade <from_token> <to_token> <amount>")
            return
        response = self.agent.trade(context.args[0], context.args[1], float(context.args[2]))
        update.message.reply_text(response)

    def track_wallet(self, update: Update, context: CallbackContext):
        """Monitors a specific wallet’s transactions."""
        if len(context.args) < 1:
            update.message.reply_text("Usage: /track_wallet <wallet_address>")
            return
        response = self.agent.track_wallet(context.args[0])
        update.message.reply_text(response)

    def post_message(self, update: Update, context: CallbackContext):
        """Manually sends a message from the bot (Admin Only)."""
        if update.message.chat_id != TELEGRAM_ADMIN_CHAT_ID:
            update.message.reply_text("This command can only be used in the admin group.")
            return
        message = " ".join(context.args)
        self.agent.send_post(TELEGRAM_ADMIN_CHAT_ID, message)
        update.message.reply_text("Message posted.")

    def post_report(self, update: Update, context: CallbackContext):
        """Posts a summary of recent market/trading activity (Admin Only)."""
        if update.message.chat_id != TELEGRAM_ADMIN_CHAT_ID:
            update.message.reply_text("This command can only be used in the admin group.")
            return
        report = self.agent.generate_report()
        update.message.reply_text(report)

    def run(self):
        """Starts the Telegram bot."""
        self.updater.start_polling()
        self.updater.idle()
