import pymongo
from celery.schedules import crontab
import csv
from pymongo import UpdateOne, InsertOne
from pymongo.errors import BulkWriteError
from app.api import log, config_env, request, DataStoreClient, tweet_search, tweet_stream, celery

@celery.task(name="tweets_search_task")
def searching(query):
    try:
        log.info("start searching for %s" % (query))
        search = tweet_search()
        search.get_tweets("#%s" % query)
        log.info("done searching")
    except Exception as e:
        log.error(e)

@celery.task(name="tweets_cursor_search_task")
def cursor_searching(query):
    try:
        log.info("start cursor searching for %s" % (query))
        search = tweet_search()
        search.get_tweets_cursor("#%s" % query)
        log.info("done searching")
    except Exception as e:
        log.error(e)

@celery.task(name="premuim_tweets_search_task")
def premuim_search(query, from_date, to_date):
    try:
        search = tweet_search()
        search.get_premuin_tweets(query, from_date, to_date)
    except Exception as e:
        log.error(e)

@celery.task(name="stream_tweets_task")
def stream_tweets(query):
    try:
        tracks_filter = ["#%s"%query]
        search = tweet_search()
        search.stream_tweets(tracks_filter)
    except Exception as e:
        log.error(e)

@celery.task(name="remove_tweets_duplicate")
def remove_tweets_duplicate():
    log.info("start removing tweets text duplicate")
    for a in DataStoreClient.tweets_collection('tweets').find({}, {'_id': 0}):
        try:
            if 'text' in a:
                DataStoreClient.tweets_collection("unique_tweets_data").insert_one(a)
            else:
                a['text'] = a['full_text']
                DataStoreClient.tweets_collection("unique_tweets_data").insert_one(a)
        except pymongo.errors.DuplicateKeyError:
            log.info("duplicate text: %s"%a['text'])
            continue
    log.info("stop removing tweets text duplicate")

@celery.task(name="extract_tweet_qoute")
def extract_tweet_qoute(collection_name):
    log.info("start extracting tweets")
    db_query = []
    for a in DataStoreClient.tweets_collection(collection_name).find({'quoted_status':{'$exists': True}}, {'_id': 0}):
        db_query.append(UpdateOne({'id_str': a['quoted_status']['id_str']}, {"$set": a['quoted_status']}, upsert=True))
    try:
        bulk_update = DataStoreClient.tweets_collection(collection_name).bulk_write(db_query)
        log.info("Insert quote tweets: %s"%bulk_update.bulk_api_result)
    except BulkWriteError as bwe:
        log.error(bwe.details)
    log.info("stop extracting tweets quote")

@celery.task(name="export_tweets")
def export_tweets(fields, collection_name):
    try:
        cursor = DataStoreClient.tweets_collection(collection_name).find(
            {},
            {
            'text': 1,
            'full_text': 1,
            'reply_count': 1,
            'retweet_count': 1,
            'favorite_count': 1,
            'source': 1,
            'created_at': 1,
            'entities.media.url': 1,
            'quote_count':1 ,
            'quoted_status.full_text': 1,
            '_id': 0,
            'id': 1
        })
        log.info(fields)
        fields = ['text', 'full_text', 'reply_count', 'retweet_count', 'favorite_count', 'source', 'created_at','entities', 'quote_count', 'quoted_status', 'id']
        with open('export/%s.csv' % collection_name, 'w') as outfile:
            write = csv.DictWriter(outfile, fieldnames=fields)
            write.writeheader()
            for record in cursor:
                write.writerow(record)
            log.info("export done")
    except Exception as e:
        log.error(e)

@celery.task(name="get_trends")
def get_trends(location_woeid=1):
    search = tweet_search()
    search.get_trends_request(location_woeid)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls every 10 seconds.
    sender.add_periodic_task(3600.0, get_trends.s(23424873), name='add every 1 hour')
    # sender.add_periodic_task(crontab(minute=4, hour='*/3'),get_trends.s(23424873), name='evry 3 hours')