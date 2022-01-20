import tkinter as tk
from tkinter import ttk

class LabeledEntry:

    def __init__(self, container, label, number, initialValue = 1):

        self.value = tk.StringVar(value=initialValue)
        ttk.Label(container, text=label).grid(column=1, row=number, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.phraseEntry = tk.Entry(container, width=3, textvariable = self.value).grid(column=0, row=number, sticky=tk.W, padx=5)

    def getEntry(self):

        return int(self.value.get())

class Frame(ttk.LabelFrame):

    def __init__(self, container, initialNumberOfPhrases = 1, initialWordsPerPhrase = 1, initialCharactersPerWord = 1):

        super().__init__(container, text='Format')

        #self.numberOfPhrases   = LabeledEntry(self, 'Phrases',             0, initialNumberOfPhrases  )
        self.wordsPerPhrase    = LabeledEntry(self, 'Words per Phrases',   1, initialWordsPerPhrase   )
        self.charactersPerWord = LabeledEntry(self, 'Characters per Word', 2, initialCharactersPerWord)

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def getEntries(self):

        entries = {}

        #entries['NumberOfPhrases']   = self.numberOfPhrases.getEntry()
        entries['WordsPerPhrase']    = self.wordsPerPhrase.getEntry()
        entries['CharactersPerWord'] = self.charactersPerWord.getEntry()

        return entries
