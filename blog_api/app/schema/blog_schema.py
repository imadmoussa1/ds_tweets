from app.api import ma


class BlogSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'content')


blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)
