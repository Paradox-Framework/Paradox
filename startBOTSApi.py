if __name__ == "__main__":
    agent = ParadoxAgent()  # Load AI agent

    # Start bots with API keys
    start_discord_bot(agent)
    start_telegram_bot(agent)
    start_twitter_bot(agent)
