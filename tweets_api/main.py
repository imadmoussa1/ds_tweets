from app.api import create_app

app = create_app()
if __name__ == '__main__':
  app.run()

  tracks_filter = ['bitcoin']
  lang = ['en']

  auth = OAuthHandler(Config.twitter_consumer_key(), Config.twitter_consumer_secret())
  auth.set_access_token(Config.twitter_access_token(),
                        Config.twitter_access_token_secret())

  listener = TweetStreamListener()
  stream = Stream(auth, listener)
  stream.filter(track=tracks_filter, languages=lang, filter_level="meduim", async="True")

