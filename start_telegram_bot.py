from telegram.ext import Updater

def start_telegram_bot(agent):
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    
    bot_handler = ParadoxTelegramBot(TELEGRAM_BOT_TOKEN, agent, int(TELEGRAM_ADMIN_CHAT_ID))
    
    bot_handler.run()
