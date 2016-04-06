'''
captures text from hiring related hashtags
'''
import tweepy
import json
from unidecode import unidecode
import HTMLParser
from keys import keys
from hashtags import *
from twitter_utils import *
import cPickle as pickle


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

with open('captured_text.txt') as f:
    lines = f.readlines()
    text_set = set(lines)


class StreamListener(tweepy.streaming.StreamListener):
    def on_connect(self):
        print("Connected to the streaming server.")

    def on_error(self, status_code):
        print('Error: ' + repr(status_code))
        return True  # Don't kill the stream

    def on_timeout(self):
        print('Timeout: keeping stream alive.')
        return True  # Don't kill the stream

    def on_data(self, data):
        try:
            incoming = json.loads(data)
            tweet = standardize_text(incoming['text'])
            user = standardize_text(incoming['user']['screen_name'])
            if any('#'+h in tweet.lower().split() for h in job_seekers):
                return
            if check_blacklist_text(tweet) or check_blacklist_user(user):
                return
            print(tweet)
            save_text(tweet)
            print('\n')
            # text = strip_tags(tweet)
            # if text:
            #     if len(text.split()) < 5:
            #         return
            #     # print(user)
            #     print(tweet)
            #     print(text)
            #     save_text(text)
            #     print('\n')
        except Exception as e:
            print(e)
            # with open('error_log.txt', 'a') as file:
            #     file.write(data)


def save_text(text):
    if text not in text_set:
        text_set.add(text)
        with open('captured_text.txt', 'a') as f:
            f.write(text.encode('utf8')+'\n')

def check_blacklist_text(text):
    blacklist = ['thinkbigsundaywithmarsha', '#career opportunity', '#career #opportunity',
                 '#careeropportunity', '#job opportunity', '#job #opportunity',
                 '#jobopportunity']
    blacklist.extend('#'+i for i in job_seekers)
    if any(i in text.lower() for i in blacklist):
        return True


def check_blacklist_user(user):
    blacklist = ['1shopforless']
    if user.lower() in blacklist:
        return True


def standardize_text(text):
    decoded = text.decode('utf8')
    unescaped = HTMLParser.HTMLParser().unescape(decoded)
    return unescaped


def main():
    while True:
        try:
            l = StreamListener()
            stream = tweepy.Stream(auth, l)
            stream.filter(track=['#'+i for i in text_capture_hashtags])
        except Exception as e:
            print e


if __name__ == '__main__':
    main()
