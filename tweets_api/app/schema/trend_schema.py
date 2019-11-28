from app.api import ma


class TrendSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'hashtag')


trend_schema = TrendSchema()
trends_schema = TrendSchema(many=True)
