import os.path
import numpy as np
import pandas as pd

class Alphabet:

    set = []

    characters = [
        ['E', 'T', 'A', 'N'],               # Session 1
        ['O', 'S', 'I', '1', '4'],          # Session 2
        ['R', 'H', 'D', 'L', '2', '5'],     # Session 3
        ['U', 'C', '.'],                    # Session 4
        ['M', 'W', '3', '6', '?'],          # Session 5
        ['F', 'Y', ','],                    # Session 6
        ['P', 'G', '7', '9', '/'],          # Session 7
        ['B', 'V', '='],                    # Session 8
        ['K', 'J', '8', '0'],               # Session 9
        ['X', 'Q', 'Z']                     # Session 10
    ]

    def __init__(self, lessons = [], letters = True, numbers = True, punctuation = True):

        if lessons:
            for lesson in lessons:
                self.set = self.set + self.characters[lesson]
        else:
            for lesson in range(0, len(self.characters), 1):
                self.set = self.set + self.characters[lesson]

    def __getitem__(self, key):
        return self.set[key]

    def __iter__(self):
        return self.set

    def getCharacters(self):
        return self.set