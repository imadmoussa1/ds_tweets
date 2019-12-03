import facebook
from .config import Config
# 46fa54372f33255f2d81acc56884feca

class FacebookApi():
    _graph = None

    def api_connected(self):
        if _graph is None:
            _graph = facebook.GraphAPI(access_token=Config.facebook_access_token(), version="3.1")
        return _graph
