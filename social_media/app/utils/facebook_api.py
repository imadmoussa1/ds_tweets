import facebook
from app.api import log, config_env, request, DataStoreClient, tweet_search, tweet_stream, celery
# 46fa54372f33255f2d81acc56884feca

class FacebookApi():
    _graph = None

    def api_connected(self):
        if _graph is None:
            _graph = facebook.GraphAPI(access_token=config_env.facebook_access_token(), version="3.1")
        return _graph

    def fb_search(self, fb_id):
        post = self.api_connected.get_object(id=fb_id)
        log.info(post)
