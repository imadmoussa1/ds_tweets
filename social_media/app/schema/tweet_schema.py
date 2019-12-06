from app.api import ma


class TweetSchema(ma.Schema):
    class Meta:
        fields = ('title', 'description', 'hashtag')


tweet_schema = TweetSchema()
tweets_schema = TweetSchema(many=True)
