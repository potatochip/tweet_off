import glob
from hashtags import *
import cPickle as pickle


def reduce_tweets()
    file_list = []
    for file in glob.glob("*.pkl"):
        file_list.append(file)

    all_tweets = set()
    for i in file_list:
        with open(i) as f:
            tweets = pickle.load(f)
            all_tweets |= tweets

    # strip new line from the rear and W/t from front
    all_tweets = [t.rstrip()[2:] for t in tweets]

    reduced_tweets = [t for t in all_tweets if any('#'+h in t.split() for h in text_capture_hashtags) and not any('#'+h in t.split() for h in job_seekers)]

    with open('hr_tweet_reduction.pkl') as f:
        pickle.dump(reduced_tweets, f)


def main():
    reduce_tweets()


if __name__ == '__main__':
    main()
