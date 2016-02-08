from nltk import sent_tokenize
from ttp import ttp
from math import log


words = open("words-by-frequency.txt").read().split()
wordcost = dict((k, log((i+1)*log(len(words)))) for i, k in enumerate(words))
maxword = max(len(x) for x in words)


def sentence_case(text):
    sentences = sent_tokenize(text)
    sentences = [x[0].upper() + x[1:] for x in sentences]
    return ' '.join(sentences)


def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""
    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k, c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1, len(s)+1):
        c, k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i > AttributeError:
        c, k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))


def strip_tags(text):
    text = text.replace('\n', ' ')

    # get rid of period sometimes placed before @username in the beginning
    if text[0] == '.':
        text = text[1:]

    if text[-3:] == '...':
        text = text[:-3]

    tokens = text.split()
    for ix, word in enumerate(tokens):
        if word == 'RT':
            tokens.pop(ix)
            try:
                tokens.pop(ix)  # try to pop what was behind the RT
            except:
                pass
    text = ' '.join(tokens)

    # remove junk at the end that is just a stream of hashtags and @'s'
    tokens = text.lower().split()
    more_slop = True
    while more_slop:
        first_char_last_token = tokens[-1][0]
        last_char_last_token = tokens[-1][-1]
        if tokens[-1].startswith('http'):
            tokens.pop()
            text = ' '.join(tokens)
        elif first_char_last_token in '.#@([' and last_char_last_token not in '.!?':
            tokens.pop()
            text = ' '.join(tokens)
        elif tokens[-1] in ['via', 'on', 'with']:
            tokens.pop()
            text = ' '.join(tokens)
        else:
            more_slop = False

    p = ttp.Parser()
    result = p.parse(text)

    for i in result.users:
        text = text.replace('@'+i, i.capitalize())

    # remove links
    for i in result.urls:
        text = text.replace(i+', ', '')
        text = text.replace(i+' ', '')
        text = text.replace(' '+i, '')
        text = text.replace(i, '')  # where tweet consists only of the link

    # remove last word if now it is via after stripping an @-name
    tokens = text.split()
    last_word = tokens[-1]
    slop = ['via', 'on', 'with']
    if last_word in slop or len(last_word) < 2:
        tokens.pop()
        text = ' '.join(tokens)

    # remove any via and the word following it
    tokens = text.split()
    if 'via' in tokens:
        ix = tokens.index('via')
        tokens.pop(ix)
        try:
            tokens.pop(ix+1)
        except:
            pass
        text = ' '.join(tokens)


    # remove junk at front of tweet
    tokens = text.split()
    more_slop = True
    while more_slop:
        first_char_first_token = tokens[0][0]
        if first_char_first_token in ['#', '@']:
            tokens.pop(0)
            text = ' '.join(tokens)
        else:
            more_slop = False

    # remove first word if it is now colon or ends in colon
    tokens = text.split()
    first_word = tokens[0]
    if first_word[-1] == ':':
        tokens.pop(0)
        text = ' '.join(tokens)

    result = p.parse(text)

    # unravel hashtags and remove hashmark
    for i in result.tags:
        unraveled = infer_spaces(i)
        text = text.replace('#'+i, unraveled)

    text = text.strip()

    if text[-1] in ':-|':
        text = text[:-1]
    if text[-1] in ['=>', ' -', '->']:
        text = text[:-2] + '.'
    if text[-1] not in '.?!':
        text = text + '.'

    return sentence_case(text.strip())
