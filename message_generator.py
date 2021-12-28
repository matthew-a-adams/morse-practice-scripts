import os.path
import numpy as np
import pandas as pd

import random

import alphabet_tools as at

class Message:

    alphabet = []

    numberOfWords = 1
    numberOfCharacters = 1

    def __init__(self, charactersPerWord = 1, wordsPerPhrase = 1, alphabet = []):

        if alphabet:
            self.alphabet = alphabet
        else:
            self.alphabet = at.Alphabet().getCharacters()

        self.numberOfWords = wordsPerPhrase
        self.numberOfCharacters = charactersPerWord

    def generateCharacter(self):
        return random.choices(self.alphabet, k=1)

    def generateWord(self, dictionary = []):

        word = []

        for character in range(0, self.numberOfCharacters, 1):
            word = word + self.generateCharacter()

        return word

    def generate(self):

        phrase = []

        for word in range(0, self.numberOfWords, 1):
            phrase.append(self.generateWord())

        return phrase
