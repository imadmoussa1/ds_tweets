import datetime
import json
import re
from nltk.tokenize import WordPunctTokenizer
from bs4 import BeautifulSoup
from textblob import TextBlob
import tweepy
# from watson_developer_cloud import ToneAnalyzerV3
from .data_store_client import DataStoreClient
from .logger import Logger

log = Logger.log(__name__)


class TweetStreamListener(tweepy.StreamListener):

    def on_data(self, data):
        tweet_dict_data = json.loads(data)
        log.info("stream tweet: %s"%tweet_dict_data['text'])
        tweet_dict_data['created_at'] = datetime.datetime.strptime(tweet_dict_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        DataStoreClient.tweets_collection('tweets').insert_one(tweet_dict_data)
        DataStoreClient.tweets_collection().update_one({'id_str': tweet_dict_data['id_str']}, {"$set": tweet_dict_data}, upsert=True)

        # # pass tweet into TextBlob
        # if tweet_dict_data['favorited'] or tweet_dict_data['retweeted'] or tweet_dict_data['user']['followers_count'] > 100000 or tweet_dict_data['user']['friends_count'] > 5000:
        #     log.debug(tweet_dict_data)
        #     if tweet_dict_data['truncated']:
        #         tweet = tweet_dict_data["extended_tweet"]['full_text']
        #         hashtags = tweet_dict_data['extended_tweet']['entities']['hashtags']
        #         user_mentions = tweet_dict_data['extended_tweet']['entities']['user_mentions']
        #     else:
        #         tweet = tweet_dict_data["text"]
        #         hashtags = tweet_dict_data['entities']['hashtags']
        #         user_mentions = tweet_dict_data['entities']['user_mentions']

        #     # filtered_tweet = ' '.join(re.sub("(@[A-Za-z0-9])|([^0-9A-Za-z \t])|(\w:\/\/\S+)", " ", tweet).split())
        #     filtered_tweet = TweetStreamListener.tweet_cleaner(tweet)
        #     # tone_analyzer = ToneAnalyzerV3(version='2017-09-21', username='2024c3cc-6366-4b8d-9a11-f0fb0b7a6dcc',password='gQF2NOGfs2q4', url='https://gateway.watsonplatform.net/tone-analyzer/api')

        #     # tone_analysis = tone_analyzer.tone({'text': filtered_tweet}, 'application/json').get_result()
        #     # log.info(json.dumps(tone_analysis, indent=2))

        #     tweet_text_blob = TextBlob(filtered_tweet)
        #     log.debug(tweet_text_blob.sentiment_assessments)
        #     # tweet_text_blob.sentiment.polarity, tweet_text_blob.sentiment.subjectivity)

        #     # determine if sentiment is positive, negative, or neutral
        #     if tweet_text_blob.sentiment.polarity < 0:
        #         sentiment = "negative"
        #     elif tweet_text_blob.sentiment.polarity == 0:
        #         sentiment = "neutral"
        #     else:
        #         sentiment = "positive"

        #     # output sentiment
        #     tweet_sentiment_obj = {
        #         'tweet_id': tweet_dict_data['id'],
        #         'filtered_tweet': filtered_tweet,
        #         "sentiment_polarity": tweet_text_blob.sentiment.polarity,
        #         "sentiment_subjectivity": tweet_text_blob.sentiment.subjectivity,
        #         'tweet': tweet,
        #         'hashtags': hashtags,
        #         'user_mentions': user_mentions,
        #         'created_at': tweet_dict_data['id'],
        #         'quote_count': tweet_dict_data['quote_count'],
        #         'reply_count': tweet_dict_data['reply_count'],
        #         'retweet_count': tweet_dict_data['retweet_count'],
        #         'favorite_count': tweet_dict_data['favorite_count'],
        #         # user info
        #         'user_id': tweet_dict_data['user']['id'],
        #         'user_name': tweet_dict_data['user']['name'],
        #         'account_description': tweet_dict_data['user']['description'],
        #         'account_url': tweet_dict_data['user']['url'],
        #         'user_followers_count': tweet_dict_data['user']['followers_count'],
        #         'account_created_at': tweet_dict_data['user']['created_at'],
        #         # location
        #         'place': tweet_dict_data['place'],
        #         'coordinates': tweet_dict_data['coordinates'],
        #         'geo': tweet_dict_data['geo'],
        #         # sentiment
        #         'sentiment': sentiment,
        #         'sentiment_assessments': tweet_text_blob.sentiment_assessments,
        #         'tone_analysis': tone_analysis,
        #         'timestamp': tweet_dict_data['timestamp_ms'],
        #         'meta': tweet_dict_data
        #     }
        #     DataStoreClient.anlyzed_tweets_collection().update_one({'tweet_id': tweet_sentiment_obj['tweet_id']}, {"$set": tweet_sentiment_obj}, upsert=True)

    # on failure
    def on_error(self, status):
        log.error(status)

    @staticmethod
    def tweet_cleaner(tweet):
        tok = WordPunctTokenizer()
        pat1 = r'@[A-Za-z_]+'
        pat2 = r'https?://[^ ]+'
        part3 = r'RT'
        combined_pat = r'|'.join((pat1, pat2, part3))
        www_pat = r'www.[^ ]+'
        negations_dic = {"isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
                         "haven't": "have not", "hasn't": "has not", "hadn't": "had not", "won't": "will not",
                         "wouldn't": "would not", "don't": "do not", "doesn't": "does not", "didn't": "did not",
                         "can't": "can not", "couldn't": "could not", "shouldn't": "should not", "mightn't": "might not",
                         "mustn't": "must not"}
        neg_pattern = re.compile(
            r'\b(' + '|'.join(negations_dic.keys()) + r')\b')

        soup = BeautifulSoup(tweet, 'lxml')
        souped = soup.get_text()
        try:
            bom_removed = souped.decode("utf-8-sig").replace(u"\ufffd", "?")
        except:
            bom_removed = souped
        stripped = re.sub(combined_pat, '', bom_removed)
        stripped = re.sub(www_pat, '', stripped)
        neg_handled = neg_pattern.sub(
            lambda x: negations_dic[x.group()], stripped)
        # letters_only = re.sub("[^a-zA-Z]", " ", neg_handled)
        words = [x for x in tok.tokenize(neg_handled) if len(x) > 1]
        return (" ".join(words)).strip()
