#!/usr/bin/env python3

from __future__ import division, print_function


import message_generator as mg

def main(characters, words, phrases):

    message = mg.Message(words, characters)

    for phrase in range (1, phrases):
        for word in message.generate():
            print(word)

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Test message generator.')

  parser.add_argument('--characters', type=int, default=1, help='Number of characters per word')
  parser.add_argument('--words', type=int, default=1, help='Number of words per phrase')
  parser.add_argument('--phrases', type=int, default=1, help='Number of phrases to generate')

  args = parser.parse_args()

  main(args.characters, args.words, args.phrases)

