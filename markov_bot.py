import tweepy
import json
from unidecode import unidecode
import HTMLParser
from twitter_utils import strip_tags


def standardize_text(text):
    decoded = unidecode(text)
    unescaped = HTMLParser.HTMLParser().unescape(decoded)
    return unescaped


class StreamListener(tweepy.streaming.StreamListener):
    def __init__(self, blacklist_text=None, blacklist_users=None):
        self.blacklist_text = blacklist_text
        self.blacklist_users = blacklist_users
        super(StreamListener, self).__init__()

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
            if not self._check_blacklist_text(tweet) and not self._check_blacklist_user(user):
                print(user)
                print(tweet)
                text = strip_tags(tweet)
                print text
                if len(text.split()) < 3:
                    print 'TOO SHORT!'
                else:
                    self._save_text(text)
                print
        except:
            pass
            # with open('error_log.txt', 'a') as file:
            #     file.write(data)

    def _save_text(self, text):
        with open('captured_text.txt', 'a') as f:
            f.write(text.encode('utf8')+'\n')

    def _check_blacklist_text(self, text):
        blacklist = self.blacklist_text
        if any(i in text.lower() for i in blacklist):
            return True

    def _check_blacklist_user(self, user):
        blacklist = self.blacklist_users
        if user.lower() in blacklist:
            return True


class MarkovBot(object):
    def __init__(self, keys, hashtags=None, users=None):
        self.keys = keys
        self.hashtags = hashtags
        self.users = users
        self.max_tweet_length = 139
        self._create_auth()

    def _create_auth(self):
        auth = tweepy.OAuthHandler(self.keys['consumer_key'], self.keys['consumer_secret'])
        auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])
        self.auth = auth

    def collect_data(self, blacklist_text=None, blacklist_users=None):
        l = StreamListener(blacklist_text, blacklist_users)
        stream = tweepy.Stream(self.auth, l)
        if self.hashtags and self.users:
            stream.filter(track=['#'+i for i in self.hashtags], follow=self.users)
        elif self.hashtags:
            stream.filter(track=['#'+i for i in self.hashtags])
        elif self.users:
            stream.filter(follow=self.users)
        else:
            stream.filter()

    def start_tweeting(self):
        pass

    def generate_samples_from_data(self, sample_n):
        pass
