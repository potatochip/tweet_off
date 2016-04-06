'''
winning
'''


from keys import keys
import tweepy
from time import sleep
import random
from unicode_csv_handler import UnicodeCsvReader
from markov_chain import MarkovChain
from hashtags import *
from twitter_utils import *
from gildit import get_content_dict
from topic_modeling import Topics


auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])

max_length = 140


def get_text():
    with open('captured_text.txt') as f:
        data = f.readlines()
    return set(data)


def tweet_out(tweet):
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


def get_topics(texts, index):
    # texts = [i['text'] for i in get_content_dict()]
    t = Topics(texts)
    return t.topics_for_document(index)


def generate_markov_sentence(original_sentence):
    mc = MarkovChain(verbose=False)
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
            return generate_seedless_markov_sentence()
    if check_blacklist(sent):
        return ''
    else:
        return sentence_case(sent)


def generate_topic_markov_sentence(texts, index):
    topics = get_topics(texts, index)
    mc = MarkovChain(verbose=False)
    mc.generateDatabase((' '.join(get_text())))
    sent = mc.generateStringWithTopics(topics)
    if check_blacklist(sent):
        return ''
    else:
        return sentence_case(sent)


def generate_seedless_markov_sentence():
    mc = MarkovChain(verbose=False)
    mc.generateDatabase((' '.join(get_text())))
    sent = mc.generateString()
    if check_blacklist(sent):
        return ''
    else:
        return sentence_case(sent)


def get_hashtags(count):
    hashtags = set()
    while len(hashtags) != count:
        hashtags.add(hashtag_randomizer())
    hashtag_string = ' '.join(hashtags)
    return ' ' + hashtag_string + ' '


def fit_length(msg, link):
    def hashtag_and_link(num_hashtags, link):
        return get_hashtags(num_hashtags) + 'via ' + link

    content_end = hashtag_and_link(1, link) if link else get_hashtags(1)
    message = msg + content_end
    msg_length = len(message) - len(link) + 23
    if msg_length > max_length:
        overrun = msg_length - max_length
        message = msg[:-overrun-3].strip() + '...' + content_end
        return message
    else:
        new_message = msg + hashtag_and_link(2, link) if link else msg + get_hashtags(2)
        new_msg_length = len(new_message) - len(link) + 23
        if new_msg_length < max_length:
            return new_message
        else:
            return message


def fix_bugs(text, insert_period=True):
    text = text.replace('\"', '').replace('\'', '')
    dirty = True
    status = True
    while dirty:
        if text:
            if text[-1] in ':-|,=>':
                text = text[:-1].strip()
            else:
                dirty = False
        else:
            dirty = False
            status = False
    if insert_period:
        if text:
            if text[-1] not in '.?!':
                text = text + '.'
    text = ' '.join(text.split())
    return text, status


def get_content():
    # with open('content.csv') as csv_file:
    #     data = UnicodeCsvReader(csv_file, skipinitialspace=True)
    #     full_data = list(data)
    # selected_content = random.choice(full_data)
    # original_sentence = selected_content[0]
    # link = selected_content[1]
    content = get_content_dict()
    index = random.choice(range(len(content)))
    selected_content = content[index]
    original_sentence = selected_content['message']
    link = selected_content['link']
    # choices = ['original'] * 40 + ['markov_seed'] * 30 + ['markov_gen'] * 30
    choices = ['original', 'markov_seed', 'markov_gen', 'markov_topic']
    # choices = ['original', 'markov_seed', 'markov_gen']
    choice = random.choice(choices)
    if choice == 'original':
        message = fit_length(original_sentence, link)
    elif choice == 'markov_seed':
        bad_tweet = True
        while bad_tweet:
            markov = generate_markov_sentence(original_sentence)
            cleaned, status = fix_bugs(markov, insert_period=False)
            bad_tweet = True if not status else False
            if not bad_tweet:
                bad_tweet = True if too_short(cleaned) else False
        message = fit_length(markov, link)
    elif choice == 'markov_gen':
        bad_tweet = True
        while bad_tweet:
            markov = generate_seedless_markov_sentence()
            cleaned, status = fix_bugs(markov, insert_period=False)
            bad_tweet = True if not status else False
            if not bad_tweet:
                bad_tweet = True if too_short(cleaned) else False
        message = fit_length(markov, "")  # no link when completely random text
        # message = markov
    elif choice == 'markov_topic':
        bad_tweet = True
        while bad_tweet:
            texts = [i['text'] for i in content]
            markov = generate_topic_markov_sentence(texts, index)
            cleaned, status = fix_bugs(markov, insert_period=False)
            bad_tweet = True if not status else False
            if not bad_tweet:
                bad_tweet = True if too_short(cleaned) else False
        message = fit_length(markov, link)
    print('{}: {}'.format(choice, message.encode('utf8')))
    return message


def too_short(s):
    if not s:
        return True
    if len(s.split()) < 3:
        print('too short: {}'.format(s.encode('utf8')))
        return True


def main():
    while True:
        try:
            msg = get_content()
            tweet_out(msg)
            sleep(random.randint(1800, 5400))
        except Exception as e:
            print('error: {}'.format(e))
            # try:
            #     tweet_out("hey boss, we have an error. i'm too lazy to be more discrete. can you check the logs?")
            #     print('error: {}'.format(e))
            # except:
            #     pass


if __name__ == '__main__':
    main()
