'''
winning
'''

from keys import keys
import tweepy
from time import sleep
import random
from unicode_csv_handler import UnicodeCsvReader
import glob
from markov_chain import MarkovChain
from hashtags import *
from twitter_utils import *


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

max_length = 139


def get_text():
    # text = ''
    # read_files = glob.glob("text/*.txt")
    # for f in read_files:
    #     with open(f, "rb") as infile:
    #         text += infile.read()
    # return text
    data = set()
    with open('catured_text.txt') as f:
        for row in f.readlines():
            data.add(row)
    return data


def tweet_out(tweet):
    print tweet
    api = tweepy.API(auth)
    api.update_status(status=tweet)


def hashtag_randomizer():
    hashtag_mark = '#'
    selected_hashtag = random.choice(list(all_hashtags))
    return hashtag_mark + selected_hashtag


def generate_markov_sentence(original_sentence):
    mc = MarkovChain()
    mc.generateDatabase((' '.join(get_text())))
    stripped = strip_tags(original_sentence)
    try:
        seed = ' '.join(stripped.split()[0:3])
        sent = mc.generateStringWithSeed(seed)
    except:
        try:
            seed = ' '.join(stripped.split()[0:2])
            sent = mc.generateStringWithSeed(seed)
        except:
            sent = mc.generateString()
    return sent


def get_hashtags(count):
    hashtags = set()
    while len(hashtags) != count:
        hashtags.add(hashtag_randomizer())
    hashtag_string = ' '.join(hashtags)
    return ' ' + hashtag_string + ' '


def fit_length(msg, link):
    content_end = get_hashtags(1) + link
    message = msg + content_end
    if len(message) > max_length:
        overrun = len(message) - max_length
        message = msg[:-overrun-3] + '...' + content_end
        return message
    else:
        new_message = msg + get_hashtags(2) + link
        if len(new_message) < max_length:
            return new_message
        else:
            return message


def get_content():
    with open('content.csv') as csv_file:
        data = UnicodeCsvReader(csv_file, skipinitialspace=True)
        full_data = list(data)
    selected_content = random.choice(full_data)
    original_sentence = selected_content[0]
    link = selected_content[1]
    choices = ['original'] * 40 + ['markov_seed'] * 30 + ['markov_gen'] * 30
    choice = random.choice(choices)
    if choice == 'original':
        message = fit_length(original_sentence, link)
    elif choice == 'markov_seed':
        markov = ''
        while len(markov.split()) < 4:
            print 'too short'
            print markov
            markov = generate_markov_sentence(original_sentence)
        message = fit_length(markov, link)
    else:
        markov = ''
        while len(markov.split()) < 4:
            print 'too short'
            print markov
            markov = generateString()
        message = fit_length(markov, link)
    return message


def main():
    while True:
        msg = get_content()
        if len(msg) < max_length:
            tweet_out(msg)
            sleep(random.randint(1800, 5400))
        else:
            print('TOO LONG: {}'.format(msg))


if __name__ == '__main__':
    main()
