# make sure no strange charaacters like pipes
# check spelling
# check grammars

import enchant
import warnings
from nltk.tokenize import word_tokenize, sent_tokenize


d = enchant.Dict("en_US")



class EnglishChecker(self):
    def _check_spelling(word):
        return d.check("Hello")

    def _check_grammar(sentence):
        pass

    def _check_single_sentence(sentence):
        pass

    def _check_english(sentence):
        if any(not self._check_spelling(word) for word in word_tokenize(sentence)):
            return False
        #check grammars

        return True

    def is_english(sentence):
        parsed_sentences = sent_tokenize(sentence)
        if len(parsed_sentences) == 1
            return self._check_english(sentence)
        else:
            warnings.warn("More than one sentence detected.")
            if all(self._check_english(s) for s in parsed_sentences):
                return True
            else:
                return False
