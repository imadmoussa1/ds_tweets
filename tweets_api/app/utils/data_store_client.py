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
        # return DataStoreClient.tweets_collection('unique_tweets_data').create_index([('text', pymongo.TEXT)], name='text_index', unique=True)
        index_name = 'id_index'
        if index_name not in DataStoreClient.tweets_collection().index_information():
            return DataStoreClient.tweets_collection().create_index([('id_str', pymongo.TEXT)], name=index_name, unique=True)

    @staticmethod
    def stream_raw_database():
        if DataStoreClient._stream_raw_database is None and DataStoreClient.is_database_connected():
            DataStoreClient._stream_raw_database = DataStoreClient.mongo_client()[Config.stream_raw_database_name()]
        return DataStoreClient._stream_raw_database

    @staticmethod
    def analyzed_database():
        if DataStoreClient._analyzed_database is None:
            DataStoreClient._analyzed_database = DataStoreClient.mongo_client()[Config.analyzed_database_name()]
        return DataStoreClient._analyzed_database

    @staticmethod
    def tweets_collection(collection_name=None):
        if collection_name is None:
            return DataStoreClient.stream_raw_database()[Config.tweets_collection_name()]
        else:
            return DataStoreClient.stream_raw_database()[collection_name]

    @staticmethod
    def anlyzed_tweets_collection():
        return DataStoreClient.analyzed_database()[Config.tweets_collection_name()]
