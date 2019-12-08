from app.api import ma


class HashtagSchema(ma.Schema):
  class Meta:
    fields = ('id', 'hashtag')


hashtag_schema = HashtagSchema()
hashtags_schema = HashtagSchema(many=True)
