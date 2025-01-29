from telegram.ext import Updater

def start_telegram_bot(agent):
    # Start Telegram bot with API key
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    
    # Load commands into bot
    bot_handler = ParadoxTelegramBot(TELEGRAM_BOT_TOKEN, agent, int(TELEGRAM_ADMIN_CHAT_ID))
    
    bot_handler.run()
