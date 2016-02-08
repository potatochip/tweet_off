'''
winning
'''
#TODO: move data into pickled set? more efficient and faster but then cant just edit in a text browser
#TODO: allow updating of content.csv files from browser. flask-admin app?
#TODO: add post to website and link to twitter page

from keys import keys
import tweepy
from time import sleep
import random
from unicode_csv_handler import UnicodeCsvReader
from markov_chain import MarkovChain
from hashtags import *
from twitter_utils import *


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

max_length = 140


def get_text():
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


def check_blacklist(sentence):
    if '"' in sentence:
        # confirm closing quote if there is an opening quote
        ix = sentence.index('"')
        try:
            if '"' not in sentence[ix+1:]:
                return True
        except:
            return True
    if 'via' in sentence:
        return True


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
    if check_blacklist(sent):
        return ''
    else:
        return sentence_case(sent + '.')


def generate_seedless_markov_sentence():
    mc = MarkovChain()
    mc.generateDatabase((' '.join(get_text())))
    sent = mc.generateString()
    if check_blacklist(sent):
        return ''
    else:
        return sentence_case(sent + '.')


def get_hashtags(count):
    hashtags = set()
    while len(hashtags) != count:
        hashtags.add(hashtag_randomizer())
    hashtag_string = ' '.join(hashtags)
    return ' ' + hashtag_string + ' '


def fit_length(msg, link):
    content_end = get_hashtags(1) + 'via ' + link
    message = msg + content_end
    msg_length = len(message) - len(link) + 23
    if msg_length > max_length:
        overrun = msg_length - max_length
        message = msg[:-overrun-3] + '...' + content_end
        return message
    else:
        new_message = msg + get_hashtags(2) + 'via ' + link
        new_msg_length = len(new_message) - len(link) + 23
        if new_msg_length < max_length:
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
    # choices = ['original'] * 40 + ['markov_seed'] * 30 + ['markov_gen'] * 30
    choices = ['original', 'markov_seed', 'markov_gen']
    choice = random.choice(choices)
    if choice == 'original':
        message = fit_length(original_sentence, link)
    elif choice == 'markov_seed':
        markov = ''
        while len(markov.split()) < 2:
            print 'too short'
            print markov
            markov = generate_markov_sentence(original_sentence)
        message = fit_length(markov, link)
    elif choice == 'markov_gen':
        markov = ''
        while len(markov.split()) < 2:
            print 'too short'
            print markov
            markov = generate_seedless_markov_sentence()
        message = fit_length(markov, link)
    return message


def main():
    while True:
        try:
            msg = get_content()
            tweet_out(msg)
            sleep(random.randint(1800, 5400))
        except Exception as e:
            print e


if __name__ == '__main__':
    main()
