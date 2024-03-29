import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from .config import Config


class DataStoreClient:
    _mongo_client = None
    _stream_raw_database = None
    _analyzed_database = None

    @staticmethod
    def mongo_client():
        if DataStoreClient._mongo_client is None:
            mongo_uri = open("/run/secrets/mongo_db_uri", "r").readline()
            DataStoreClient._mongo_client = MongoClient(mongo_uri)
        return DataStoreClient._mongo_client

    @staticmethod
    def is_database_connected():
        try:
            DataStoreClient.mongo_client().admin.command('ismaster')
            return True
        except ConnectionFailure:
            return False

    @staticmethod
    def create_index():
        index_name = 'title_index'
        if index_name not in DataStoreClient.blog_drafts_collection().index_information():
            return DataStoreClient.blog_drafts_collection().create_index([('title', pymongo.TEXT)], name=index_name, default_language='english')

    @staticmethod
    def stream_raw_database():
        if DataStoreClient._stream_raw_database is None and DataStoreClient.is_database_connected():
            print(DataStoreClient.mongo_client())
            DataStoreClient._stream_raw_database = DataStoreClient.mongo_client()[Config.stream_raw_database_name()]
        return DataStoreClient._stream_raw_database

    @staticmethod
    def analyzed_database():
        if DataStoreClient._analyzed_database is None:
            DataStoreClient._analyzed_database = DataStoreClient.mongo_client()[Config.analyzed_database_name()]
        return DataStoreClient._analyzed_database

    @staticmethod
    def tweets_collection():
        return DataStoreClient.stream_raw_database()[Config.tweets_collection_name()]

    @staticmethod
    def anlyzed_tweets_collection():
        return DataStoreClient.analyzed_database()[Config.tweets_collection_name()]
