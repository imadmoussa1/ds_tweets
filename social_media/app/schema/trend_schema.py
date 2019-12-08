from app.api import ma


class TrendSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'url', 'promoted_content', 'query', 'tweet_volume')


trend_schema = TrendSchema()
trends_schema = TrendSchema(many=True)
