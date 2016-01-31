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


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

max_length = 140


# def get_text():
#     text = ''
#     read_files = glob.glob("text/*.txt")
#     for f in read_files:
#         with open(f, "rb") as infile:
#             text += infile.read()
#     return text

# mc = MarkovChain()
# mc.generateDatabase(get_text())


def tweet_out(tweet):
    print tweet
    api = tweepy.API(auth)
    api.update_status(status=tweet)


def hashtag_randomizer():
    hashtag_mark = '#'
    selected_hashtag = random.choice(list(all_hashtags))
    return hashtag_mark + selected_hashtag


def check_sentence_length(sent, max_length):
    if len(sent) > max_length:
        return False
    else:
        return True


def check_sentence_grammar(sent):
    pass


def generate_markov_sentence(original_sentence, remaining_length):
    valid_sent = False
    seed = ' '.join(original_sentence.split()[0:2])
    while not valid_sent:
        sent = mc.generateStringWithSeed(seed)
        valid_sent = check_sentence_length(sent, remaining_length)
        # if valid_sent:
        #     valid_sent = check_sentence_grammar(sent)
    return sent


def get_content():
    with open('content.csv') as csv_file:
        data = UnicodeCsvReader(csv_file, skipinitialspace=True)
        full_data = list(data)
    selected_content = random.choice(full_data)
    original_sentence = selected_content[0]
    link = selected_content[1]
    content_end = ' ' + hashtag_randomizer() + ' ' + link
    remaining_length = max_length - len(content_end)
    # message = generate_markov_sentence(original_sentence, remaining_length)
    # return message + content_end
    message = original_sentence + content_end
    return message


def main():
    while True:
        msg = get_content()
        if len(msg) < max_length:
            tweet_out(msg)
            sleep(random.randint(1800, 7200))
        else:
            print('TOO LONG: {}'.format(msg))


if __name__ == '__main__':
    main()

recreate markovchain every tweet so it always stays updated. read captured.text and then dump the sentences into a set so identicals are dropped.
randomly use the markov sentence some percentage of the time and the other percentage use the original sentence
make sure sentence plus one hashtag does not run over limit. if much less than original then add a second or third hashtag
