import os


# Configuration class to load environments variables
class Config(object):
    _sqlalchemy_database_uri = None
    _debug = None
    _testing = None
    _wtf_csrf_enabled = None
    _log_level = None
    _bcrypt_log_rounds = None
    _secret_key = None
    _jwt_secret_key = None
    _twitter_consumer_key = None
    _twitter_consumer_secret = None
    _twitter_access_token = None
    _twitter_access_token_secret = None
    _stream_raw_database_name = None
    _analyzed_database_name = None
    _redis_uri = None
    _tweets_collection_name = None

    @staticmethod
    def sqlalchemy_database_uri():
        if Config._sqlalchemy_database_uri is None:
            Config._sqlalchemy_database_uri = open("/run/secrets/postgres_db_uri", "r").readline()
        return Config._sqlalchemy_database_uri

    @staticmethod
    def redis_uri():
        if Config._redis_uri is None:
            Config._redis_uri = os.getenv('REDIS_URI', 'redis://redis:6379')
        return Config._redis_uri

    @staticmethod
    def log_level():
        if Config._log_level is None:
            Config._log_level = os.getenv('LOG_LEVEL', 'INFO')
        return Config._log_level

    @staticmethod
    def secret_key():
        if Config._secret_key is None:
            Config._secret_key = os.getenv('SECRET_KEY', "7B968F7F2E7FA3FE577FD97C4DADA")
        return Config._secret_key

    @staticmethod
    def jwt_secret_key():
        if Config._jwt_secret_key is None:
            Config._jwt_secret_key = os.getenv('JWT_SECRET_KEY', "7B968F7F2E7FA3FE577FD97C4DADA")
        return Config._jwt_secret_key

    @staticmethod
    def bcrypt_log_rounds():
        if Config._bcrypt_log_rounds is None:
            Config._bcrypt_log_rounds = os.getenv('BCRYPT_LOG_ROUNDS', "15")
        return Config._bcrypt_log_rounds

    @staticmethod
    def testing():
        if Config._testing is None:
            Config._testing = os.getenv('TESTING', False)
        return Config._testing

    @staticmethod
    def debug():
        if Config._debug is None:
            Config._debug = os.getenv('DEBUG', True)
        return Config._debug

    @staticmethod
    def database_service_name():
        if Config._database_service_name is None:
            Config._database_service_name = os.getenv('MONGO_NAME', 'mongo')
        return Config._database_service_name

    @staticmethod
    def database_service_port():
        if Config._database_service_port is None:
            Config._database_service_port = int(os.getenv('MONGO_PORT', 27017))
        return Config._database_service_port

    @staticmethod
    def log_level():
        if Config._log_level is None:
            Config._log_level = os.getenv('LOG_LEVEL', 'INFO')
        return Config._log_level

    @staticmethod
    def stream_raw_database_name():
        if Config._stream_raw_database_name is None:
            Config._stream_raw_database_name = os.getenv('STREAM_RAW_DATABASE_NAME', 'stream_raw_data')
        return Config._stream_raw_database_name

    @staticmethod
    def analyzed_database_name():
        if Config._analyzed_database_name is None:
            Config._analyzed_database_name = os.getenv('ANALYZED_DATABASE_NAME', 'analyzed_data')
        return Config._analyzed_database_name

    @staticmethod
    def tweets_collection_name():
        if Config._tweets_collection_name is None:
            Config._tweets_collection_name = os.getenv('TWEETS_COLLECTION_NAME', 'tweets')
        return Config._tweets_collection_name

    @staticmethod
    def twitter_consumer_key():
        if Config._twitter_consumer_key is None:
            Config._twitter_consumer_key = os.getenv('TWITTER_CONSUMER_KEY', '')
        return Config._twitter_consumer_key

    @staticmethod
    def twitter_consumer_secret():
        if Config._twitter_consumer_secret is None:
            Config._twitter_consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET', '')
        return Config._twitter_consumer_secret

    @staticmethod
    def twitter_access_token():
        if Config._twitter_access_token is None:
            Config._twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
        return Config._twitter_access_token

    @staticmethod
    def twitter_access_token_secret():
        if Config._twitter_access_token_secret is None:
            Config._twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        return Config._twitter_access_token_secret

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
