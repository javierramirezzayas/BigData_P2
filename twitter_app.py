import socket
import sys
import json
import tweepy
from tweepy import OAuthHandler

# Replace the values below with yours
consumer_key = "H0rHI7rViOR0tkbN5Q468RXnY"
consumer_secret = "7YE8T5dDmJ8Z9Bl4G67f7PTf647pM7Z06FspDyHJJoGVlmozlp"
access_token = "1065611139504095233-5VHWzb00YCxll8kqrX9PO0M6Yuvd7l"
access_secret = "M5EjfU8Lc4ougpfSyADtK0d8khcJDeUapK9FsUmTnSJpw"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        send_tweets_to_spark(json.dumps(status._json), conn)
        # print(json.dumps(status._json))

    def on_error(self, status_code):
        if status_code == 420:
            return False


def send_tweets_to_spark(resp, tcp_connection):
    try:
        full_tweet = json.loads(resp)
        tweet_text = full_tweet['text']
        user = full_tweet['user']
        user_name = user['screen_name']
        # print("Tweet Text: " + tweet_text)
        # print("User_Name: " + user_name)
        text = user_name + "|||" + tweet_text + '\n'
        print(text)
        tcp_connection.send(text.encode('utf-8'))
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


TCP_IP = "localhost"
TCP_PORT = 9009
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn = None
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=["a", "the", "i", "you", "u"], languages=["en"])
