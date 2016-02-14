import glob
import os
from hashtags import *
from progressbar import ProgressBar
import cPickle as pickle


current_dir = os.getcwd()

directory = "/Volumes/Data\ Store/all_tweets_for_six_months"
os.chdir(directory)
file_list = []
for file in glob.glob("*.txt"):
    file_list.append(file)

os.chdir(current_dir)

pbar = ProgressBar()
for index, filename in enumerate(file_list):
    corpus = set()
    with open(directory + filename) as f:
        print directory + filename
        for ix, line in enumerate(pbar(f)):
            if ix == 0: print line
            if line[0] == 'W':
                if any("#"+h in line.lower() for h in all_hashtags):
                    corpus.add(line)
    with open('hr_tweets_{}.pkl'.format(index), 'w') as f:
        pickle.dump(corpus, f)
