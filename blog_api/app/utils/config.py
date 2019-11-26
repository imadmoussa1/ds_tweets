import os


# Configuration class to load environments variables
class Config(object):
    _filter_service_name = None
    _filter_service_grpc_port = None
    _sqlalchemy_database_uri = None
    _debug = None
    _testing = None
    _wtf_csrf_enabled = None
    _log_level = None
    _bcrypt_log_rounds = None
    _secret_key = None
    _jwt_secret_key = None
    _blog_database_name = None
    _blog_drafts_collection_name = None

    @staticmethod
    def sqlalchemy_database_uri():
        if Config._sqlalchemy_database_uri is None:
            Config._sqlalchemy_database_uri = open("/run/secrets/postgres_db_uri", "r").readline()
        return Config._sqlalchemy_database_uri

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
            Config._database_service_name = os.getenv('MAIN_DATASTORE_SERVICE_NAME', 'main-data-store')
        return Config._database_service_name

    @staticmethod
    def database_service_port():
        if Config._database_service_port is None:
            Config._database_service_port = int(os.getenv('MAIN_DATASTORE_SERVICE_MONGO_PORT', 27017))
        return Config._database_service_port

    @staticmethod
    def blog_database_name():
        if Config._blog_database_name is None:
            Config._blog_database_name = os.getenv('BLOG_DATABASE_NAME', 'blog_data')
        return Config._blog_database_name

    @staticmethod
    def blog_drafts_collection_name():
        if Config._blog_drafts_collection_name is None:
            Config._blog_drafts_collection_name = os.getenv('BLOG_DRAFTS_COLLECTION_NAME', 'blog_drafts')
        return Config._blog_drafts_collection_name


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
