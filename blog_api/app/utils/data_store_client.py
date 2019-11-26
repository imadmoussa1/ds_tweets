import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from .config import Config


class DataStoreClient:
    _mongo_client = None
    _blog_database = None

    @staticmethod
    def mongo_client():
        if DataStoreClient._mongo_client is None:
            mongo_uri = open("/run/secrets/main_data_store_db_uri", "r").readline()
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
    def blog_database():
        if DataStoreClient._blog_database is None:
            DataStoreClient._blog_database = DataStoreClient.mongo_client()[Config.blog_database_name()]
        return DataStoreClient._blog_database

    @staticmethod
    def blog_drafts_collection():
        return DataStoreClient.blog_database()[Config.blog_drafts_collection_name()]

    @staticmethod
    def create_index():
        index_name = 'title_index'
        if index_name not in DataStoreClient.blog_drafts_collection().index_information():
            return DataStoreClient.blog_drafts_collection().create_index([('title', pymongo.TEXT)], name=index_name, default_language='english')
