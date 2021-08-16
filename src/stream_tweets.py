from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import boto3
import time
import configparser

config = configparser.ConfigParser()
config.read('../credentials.cfg')
consumer_key =  config['TWITTER']['API_KEY']
consumer_secret = config['TWITTER']['API_SECRET_KEY']
access_token =  config['TWITTER']['ACCESS_TOKEN']
access_token_secret =  config['TWITTER']['ACCESS_TOKEN_SECRET']

aws_access_key_id = config['AWS']['AWS_ACCESS_KEY_ID']
aws_secret_access_key = config['AWS']['AWS_SECRET_ACCESS_KEY']


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        try:
            res = client.put_record(
                DeliveryStreamName=delivery_stream,
                Record={
                'Data': data
                }
            )
            print(res['ResponseMetadata'])
        except (AttributeError, Exception) as e:
                print ("Error",e)
        return True

    def on_error(self, status):
        print (status)

if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #tweets = Table('tweets_ft',connection=conn)
    client = boto3.client('firehose',
                          region_name='ap-northeast-1',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key
                          )

    delivery_stream = 'stream_tweets_firehose'
    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    #stream.filter(track=['trump'], stall_warnings=True)
    while True:
        try:
            print('Twitter streaming...')
            stream = Stream(auth, listener)
            stream.filter(track=['bolsonaro'], stall_warnings=True)
        except Exception as e:
            print(e)
            print('Disconnected...')
            time.sleep(5)
            continue