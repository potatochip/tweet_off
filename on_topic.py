#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from ttp import ttp
import random
import nltk
from progressbar import ProgressBar
from markov_chain import MarkovChain
from gildit import get_content_dict
from hashtags import *


parser = ttp.Parser()
MAX_LENGTH = 140


class MarkovTweet(object):
    '''
    v1.1 of the string generator
    '''
    def __init__(self, db_path='markov.db'):
        self.db_path = db_path

    def generate_database(self, captured_text_path='captured_raw_text.txt'):
        p = PrepareText()
        with open(captured_text_path) as f:
            raw_text = f.readlines()
        print('Preparing texts')
        pbar = ProgressBar()
        prepared_texts = [p.prepare(i) for i in pbar(raw_text)]
        clean_texts = set(filter(lambda x: not self._drop(x) if x else False, prepared_texts))
        print('Generating database')
        mc = MarkovChain(self.db_path, verbose=False)
        mc.generateDatabase('\n'.join(clean_texts), n=4, make_lowercase=True)
        mc.dumpdb()
        self.markov = mc

    def initialize_database(self):
        mc = MarkovChain(self.db_path, verbose=False)
        self.markov = mc

    @staticmethod
    def _drop(text):
        tokens = text.split()
        word_count = len(tokens)
        if word_count < 2:
            return True
        link_count = tokens.count('<link>')
        hashtag_count = sum(1 for i in tokens if i[0] == '#')
        if (link_count + hashtag_count) / word_count >= 0.5:
            return True
        if word_count - link_count - hashtag_count < 3:
            return True

        try:
            # skip it if it ends in elipses
            tokens = text.split()
            last_word = tokens[-1]
            elipses = [u'...', u'\u2026']
            if any(i in last_word for i in elipses):
                return True

            # skip it if it begins with punctuation
            first_word = tokens[0]
            if first_word[0] in u'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~“':
                return True

            # skip it if the last word is a single letter
            if len(last_word) < 2:
                return True
        except:
            return True

    def generate_string(self):
        while True:
            gen_text = self.markov.generateString()
            if self._drop(gen_text):
                continue
            if self._check_links_and_hashtags(gen_text):
                continue
            if gen_text:
                text = self._insert_hashtags(gen_text)
                text = self._insert_links(text)
                return self.truecase(text)

    @staticmethod
    def _check_links_and_hashtags(text):
        link_count = text.count('<link>')
        parsed = parser.parse(text)
        hashtag_count = len(parsed.tags)
        word_count = len([i for i in text.split() if i != '<link>' or i not in parsed.tags])
        if link_count > word_count:
            return True
        if hashtag_count > word_count:
            return True
        if word_count == 0:
            return True

    def _insert_links(self, s):
        link_count = s.count('<link>')
        if link_count:
            s.replace('<link>', self._link_generator())
            return s
        else:
            return self._fit_link(s)

    def _insert_hashtags(self, s):
        parsed = parser.parse(s)
        if not parsed.tags:
            self._fit_hashtag(s)
        else:
            return s

    def _hashtag_generator(self, count):
        def hashtag_randomizer():
            hashtag_mark = '#'
            selected_hashtag = random.choice(list(all_hashtags))
            return hashtag_mark + selected_hashtag
        hashtags = set()
        while len(hashtags) != count:
            hashtags.add(hashtag_randomizer())
        hashtag_string = ' '.join(hashtags)
        return ' ' + hashtag_string + ' '

    def _fit_hashtag(self, msg):
        tags = self._hashtag_generator(2)
        message = msg + ' ' + tags
        msg_length = len(message)
        if msg_length > MAX_LENGTH:
            overrun = msg_length - MAX_LENGTH
            message = msg[:-overrun-3].strip() + '... ' + tags
            return message
        else:
            return message

    def _fit_link(self, msg):
        link = self._link_generator()
        message = msg + ' ' + link
        msg_length = len(message) - len(link) + 23
        if msg_length > MAX_LENGTH:
            overrun = msg_length - MAX_LENGTH
            message = msg[:-overrun-3].strip() + '... ' + link
            return message
        else:
            return message

    def _link_generator(self):
        content = get_content_dict()  # keeping it fresh
        index = random.choice(range(len(content)))
        selected_content = content[index]
        link = selected_content['link']
        return link

    @staticmethod
    def truecase(text):
        text = text.lower()
        text = re.sub(r"(\A\w)|"+             # start of string
                      "(?<!\.\w)([\.?!] )\w|"+     # after a ?/!/. and a space, but not after an acronym
                      "\w(?:\.\w)|"+               # start/middle of acronym
                      "(?<=\w\.)\w",               # end of acronym
                      lambda x: x.group().upper(),
                      text)
        sents = nltk.sent_tokenize(text) # list of sentences
        truecased_sents = [] # list of truecased sentences
        for sent in sents:
            # apply POS-tagging
            tagged_sent = nltk.pos_tag([word for word in sent.split()])
            # infer capitalization from POS-tags
            # normalized_sent = [w.capitalize() if t in ["NN","NNS"] else w for (w,t) in tagged_sent]
            normalized_sent = [w.capitalize() if t in ["NNP","NNPS"] else w for (w,t) in tagged_sent]
            # use regular expression to get punctuation right
            pretty_string = re.sub(" (?=[\.,'!?:;])", "", ' '.join(normalized_sent))
            truecased_sents.append(pretty_string)
        return ' '.join(truecased_sents)


class PrepareText(object):
    def prepare(self, text):
        self.text = text
        self.fix_raw_unicode()
        self.symbolize_links()
        self.pop_users()
        self.remove_slop()
        return self.text

    def fix_raw_unicode(self):
        text = self.text
        encoded = unicode(text, 'utf8')
        regex = re.compile(r'<\S+>', re.IGNORECASE)  # emoticons get turned into just their code
        for i in re.findall(regex, text):
            code = i[3:-1]
            try:
                charcode = '\U' + u'0'*(8-len(code)) + code
                encoded = encoded.replace(i, charcode.decode('unicode_escape'))
            except:
                pass
        self.text = encoded

    def symbolize_links(self):
        text = self.text
        result = parser.parse(text)
        for i in result.urls:
            text = text.replace(i, '<link>')
        self.text = text

    def pop_users(self):
        text = self.text

        spam_artists = ['Gordon Tredgold']
        for spam in spam_artists:
            text = text.replace(spam, '')

        # remove rt and via and whatever followed it
        new_tokens = []
        last_word_rt = False
        for word in text.split():
            if last_word_rt is True:
                last_word_rt = False
            elif word.lower() in ['rt', '(rt', '.rt', 'via']:
                last_word_rt = True
            else:
                new_tokens.append(word)
                last_word_rt = False
        text = ' '.join(new_tokens)

        result = parser.parse(text)
        for i in result.users:
            text = text.replace('@'+i, '')
        self.text = text

    def remove_slop(self):
        slop = [u'via', u'on', u'with', u'at', u'@', u'in', u'-', u'for', u'~', u'by', u'=>', u'/w', u'\\w', u'like', u'from', u'of', u'http', u'https']
        text = self.text
        try:
            # get rid of period sometimes placed before @username in the beginning
            if text[0] == '.':
                text = text[1:]
            # remove first word if it is now colon or ends in colon
            tokens = text.split()
            first_word = tokens[0]
            if first_word[-1] == ':':
                tokens.pop(0)
            # remove last word if it doesnt make any sense now
            last_word = tokens[-1]
            if last_word.lower() in slop or len(last_word) < 2:
                tokens.pop()
            text = ' '.join(tokens)
        except Exception as e:
            # print(e)
            self.text = None
        else:
            text = text.replace('\"', '')
            self.text = ' '.join(text.split())  # cleans up any weird spaces

            # correct punctuation
            punc = '.,!?:'
            for i in punc:
                self.text = self.text.replace(' '+i, i)


class MarkovOnTopic(object):
    '''
    TODO: ngrams bumped to four or five-grams
    TODO: first ngram is the technical noun topic of the tweet
    TODO: stem the topics to narrow them. or even better find a way to standardize synonyms to the same word and then stem
    TODO: db key has no hashmarks but the values do
    TODO: db key in lowercase, but values are original
    '''
    def __init__(self, db_path='markov.db'):
        try:
            self.mc = MarkovChain(db_path, verbose=False)
        except:
            print('No database found at path. Creating new database.')
            self.mc = seed_db(db_path)

    def generate_db(self, docs, filename=None):
        self.docs = docs
        pass

    def generate_topics(self):
        pass

    def generate_string(self, seed=None):
        regen = True
        while regen:
            if seed:
                gen_text = self.mc.generateStringWithSeed(seed)
            else:
                gen_text = self.mc.generateString()
            if not drop(gen_text):
                print gen_text
                regen = False
