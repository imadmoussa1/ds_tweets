from app.api import ma


class BlogDraftSchema(ma.Schema):
    class Meta:
        fields = ('title', 'description', 'content')


blog_draft_schema = BlogDraftSchema()
blog_drafts_schema = BlogDraftSchema(many=True)
