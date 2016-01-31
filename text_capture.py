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


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])


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
            if not check_blacklist_text(tweet) and not check_blacklist_user(user):
                print(user)
                print(tweet)
                text = strip_tags(tweet)
                print text
                if len(text.split()) < 3:
                    print 'TOO SHORT!'
                else:
                    save_text(text)
                print
        except:
            pass
            # with open('error_log.txt', 'a') as file:
            #     file.write(data)


def save_text(text):
    with open('catured_text.txt', 'a') as f:
        f.write(text.encode('utf8')+'\n')


def check_blacklist_text(text):
    blacklist = ['thinkbigsundaywithmarsha', '#career #opportunity', '#job #opportunity']
    if any(i in text.lower() for i in blacklist):
        return True


def check_blacklist_user(user):
    blacklist = ['1shopforless']
    if user.lower() in blacklist:
        return True


def standardize_text(text):
    decoded = unidecode(text)
    unescaped = HTMLParser.HTMLParser().unescape(decoded)
    return unescaped


def main():
    l = StreamListener()
    stream = tweepy.Stream(auth, l)
    stream.filter(track=['#'+i for i in text_capture_hashtags])


if __name__ == '__main__':
    main()
