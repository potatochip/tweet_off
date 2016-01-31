#!/usr/bin/python

# Inspired by an example from Peter Norvig, see http://norvig.com/python-lisp.html

"""Module to generate random sentences from a grammar.  The grammar consists of
entries that can be written as S = 'NP VP | S and S', which gets translated to
{'S': [['NP', 'VP'], ['S', 'and', 'S']]}, and means that one of the top-level
lists will be chosen at random, and then each element of the second-level list
will be rewritten; if it is not in the grammar it rewrites as itself.  The
functions rewrite and rewrite_tree take as input a list of words and an
accumulator (empty list) to which the results are appended.  The function
generate and generate_tree are convenient interfaces to rewrite and rewrite_tree
that accept a string (which defaults to 'S') as input."""


import random
from pprint import pprint
import sys, resource
import argparse                   # argparse is standard in 2.7

# A drawback of this simple recursive program is that, since python
# doesn't recognize tail recursion, deeply recursive programs can run
# out of stack space. So w increase max stack size from 8MB to 16MB
# and recursion limit to 1M!  You may have to coment out these lines
# if you are on a mac and have not reset the limts.

resource.setrlimit(resource.RLIMIT_STACK, (2**24,-1))
sys.setrecursionlimit(10**6)


def load_grammar(file):
    """Load a grammar from a file and return it as a dictionary. The
     keys are the grammar's non-terminal symbols and their values are
     lists of possible rewrites, where each rewrite is a (possibly
     empty) list of symbols. Example: {'S':[['S', 'and', 'S'],
     ['NP','VP']],...}"""
    grammar = {}
    for line in open(file):
        line = line.strip()
        # skip blank lines and lines beginning with hash
        if line and line[0] != '#':
            # line is like:  NP -> Art NP | Art Adj NP
            lhs, rhs = line.split('->')
            lhs = lhs.strip()
            rhs = [alt.split() for alt in rhs.strip().split('|')]
            # add the new RHS options to any exisiting ones
            grammar[lhs] = grammar.get(lhs,[]) + rhs
    return grammar


def rewrite(g, words, into):
  """Replace each word in the list with a random entry in grammar g
  (recursively)."""
  for word in words:
    if word in g:
        rewrite(g, random.choice(g[word]), into)
    else:
        into.append(word)
  return into


def rewrite_tree(g, words, into):
  """Replace the list of words into a random tree, chosen from grammar
  g."""
  for word in words:
    if word in g:
      into.append({word: rewrite_tree(g, random.choice(g[word]), [])})
    else:
      into.append(word)
  return into


def generate(g, start='S'):
  """Replace each word in str by a random entry in grammar g
  (recursively)."""
  return ' '.join(rewrite(g, [start] , []))


def generate_tree(g, start='S'):
  """Use grammar g to rewrite the category cat.  returns something
  like a parse tree."""
  return rewrite_tree(g, [start], [])


# what to do if called as a script
if __name__ == "__main__":
    # process command line arguments
    parser = argparse.ArgumentParser(description='Generate a random string from a grammar')
    parser.add_argument('-t', action="store_true", default=False,
                         help='return sentence as a tree rather than a string')
    parser.add_argument('-g', action="store", dest="gfile", required=True,
                        help='A file path specifying the grammar')
    parser.add_argument('-s', action="store", dest="start", default="S",
                        help="The grammar's start symbol for the grammar, defaults to S")
    args = parser.parse_args()

    if args.t:
        pprint(generate_tree(load_grammar(args.gfile), args.start))
    else:
        print generate(load_grammar(args.gfile), args.start)
