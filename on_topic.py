'''
ngrams bumped to four or five-grams
first ngram is the technical noun topic of the tweet

'''
import re
from ttp import ttp
from collections import defaultdict


parser = ttp.Parser()


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
            encoded = encoded.replace(i, charcode.decode('unicode_escape'))
        self.text = encoded

    def symbolize_links(self):
        text = self.text
        result = parser.parse(text)
        for i in result.urls:
            text = text.replace(i, '<link>')
        self.text = text

    def pop_users(self):
        text = self.text
        result = parser.parse(text)
        for i in result.users:
            text = text.replace('@'+i, '')
        self.text = text

    def remove_slop(self):
        text = self.text
        # get rid of period sometimes placed before @username in the beginning
        if text[0] == '.':
            text = text[1:]

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

        # remove first word if it is now colon or ends in colon
        tokens = text.split()
        first_word = tokens[0]
        if first_word[-1] == ':':
            tokens.pop(0)
            text = ' '.join(tokens)

        text = text.replace('\"', '')
        self.text = text.strip()


class MarkovOnTopic(object):
    def generate_db(self, docs, filename=None):
        self.docs = docs
        pass

    def generate_topics(self):
        pass

    def generate_string(self, seed=None):
        pass
