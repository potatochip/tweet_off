import re
from ttp import ttp
from progressbar import ProgressBar
from markov_chain import MarkovChain


parser = ttp.Parser()


def drop(text):
    # decide whether to drop a text
    tokens = text.split()
    word_count = len(tokens)
    link_count = tokens.count('<link>')
    hashtag_count = sum(1 for i in tokens if i[0] == '#')
    if (link_count + hashtag_count) / word_count > 0.5:
        return True


def seed_db(filename):
    p = PrepareText()
    with open(filename) as f:
        raw_text = f.readlines()
    print('Preparing texts')
    pbar = ProgressBar()
    prepared_texts = [p.prepare(i) for i in pbar(raw_text)]
    clean_texts = set(filter(lambda x: not drop(x) if x else False, prepared_texts))
    print('Generating database')
    mc = MarkovChain('markov.db')
    mc.generateDatabase('\n'.join(clean_texts), n=3)  # increase to 4grams once have more data
    mc.dumpdb()


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
        match_indices = [(m.start(0), m.end(0)) for m in re.finditer(regex, tweet2)]
        for i in re.findall(regex, text):
            code = i[3:-1]
            charcode = '\U' + u'0'*(8-len(code)) + code
            try:
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
            if last_word_rt == True:
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
            last_word = tokens[-1]
            if first_word[-1] == ':':
                tokens.pop(0)
            # remove last word if elipses
            elipses = [u'...', u'\u2026']
            elipses_ix = max([last_word.rfind(i) for i in elipses])
            new_last = last_word[:elipses_ix] if elipses_ix != -1 else last_word
            tokens.pop()
            tokens.append(new_last)
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
            punc = '.,!?'
            for i in punc:
                self.text = self.text.replace(' '+i, i)


class MarkovOnTopic(object):
    '''
    TODO: ngrams bumped to four or five-grams
    TODO: first ngram is the technical noun topic of the tweet
    TODO: stem the topics to narrow them. or even better find a way to standardize synonyms to the same word and then stem
    '''
    def generate_db(self, docs, filename=None):
        self.docs = docs
        pass

    def generate_topics(self):
        pass

    def generate_string(self, seed=None):
        pass
