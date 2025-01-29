import tweepy

def start_twitter_bot(agent):
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    
    api = tweepy.API(auth)
    
    twitter_bot = ParadoxTwitterBot(api, agent, TWITTER_ADMIN_HANDLE)
    twitter_bot.run()
