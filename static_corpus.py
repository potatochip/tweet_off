import glob
from hashtags import *
import cPickle as pickle
import twitter_utils
from multiprocessing import Pool
from HTMLParser import HTMLParser
from text_capture import check_blacklist_text


def combine_old_text():
new_text = set()
with open('catured_text.txt') as f:
    for tweet in f.readlines():
        if any('#'+h in tweet.lower().split() for h in job_seekers):
            continue
        if check_blacklist_text(tweet):
            continue
        text = twitter_utils.strip_tags(tweet)
        if text:
            if len(text.split()) < 5:
                continue
            new_text.add(text)
    return new_text


def reduce_tweets():
    file_list = []
    for file in glob.glob("tweets/*.pkl"):
        file_list.append(file)

    all_tweets = set()
    for i in file_list:
        with open(i) as f:
            tweets = pickle.load(f)
            all_tweets |= tweets

    # strip new line from the rear and W/t from front
    all_tweets = [t.rstrip()[2:] for t in all_tweets]

    internet_text_correction = lambda x: HTMLParser().unescape(x.decode('utf8'))

    reduced_tweets = [internet_text_correction(t) for t in all_tweets
                      if any('#'+h in t.split() for h in text_capture_hashtags) and
                      not any('#'+h in t for h in job_seekers)]

    # with open('hr_tweet_reduction_no_jobseeker_hashtags.pkl', 'w') as f:
    #     pickle.dump(reduced_tweets, f)

    pool = Pool()
    cleaned_tweets = pool.map(twitter_utils.strip_tags, reduced_tweets)

    with open('clean_hr_tweets.pkl', 'w') as f:
        pickle.dump(filter(None, cleaned_tweets), f)


def main():
    reduce_tweets()


if __name__ == '__main__':
    main()
