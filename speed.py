import tkinter as tk
from tkinter import ttk

class LabeledEntry:

    def __init__(self, container, label, number, initialValue = 1):

        self.value = tk.StringVar(value=initialValue)
        ttk.Label(container, text=label).grid(column=1, row=number, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.phraseEntry = tk.Entry(container, width=3, textvariable = self.value).grid(column=0, row=number, sticky=tk.W, padx=5)

    def getEntry(self):

        return self.value.get()

class Frame(ttk.LabelFrame):

    def __init__(self, container, initialWordsPerMinute = 25, initialFarnsworthSpeed = 4):

        super().__init__(container, text='Speed')

        self.wordsPerMinute  = LabeledEntry(self, 'Words per Minute (WPM)', 0, initialWordsPerMinute )
        self.farnsworthSpeed = LabeledEntry(self, 'Farnsworth Speed (FS)',  1, initialFarnsworthSpeed)

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def getEntries(self):

        entries = {}

        entries['WordsPerMinute']  = self.wordsPerMinute.getEntry()
        entries['FarnsworthSpeed'] = self.farnsworthSpeed.getEntry()

        return entries