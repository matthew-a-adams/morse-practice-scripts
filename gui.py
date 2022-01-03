import os

import matplotlib.pyplot as plt
import pandas as pd
import sounddevice as sd
import soundfile as sf
import tkinter as tk

from tkinter import ttk

class window(tk.Tk):

    def __init__(self, word, recordingName):
        super().__init__()

        self.recordingFileName = str(recordingName) + '.wav'

        self.word = word

        # configure the root window
        self.title('Morse Study Tool')

        # label
        frame = ttk.Frame(self)

        self.instructionLabel = ttk.Label(frame, text='Check each correctly reported letter from your recording.')
        self.instructionLabel.pack(side='left', fill='x')

        frame.grid(column=0, row=0, ipadx=5, pady=5, sticky=tk.N)

        # checkboxes
        frame = ttk.Frame(self)

        self.checkButtonVar = []
        for i in range(0, len(self.word)):
            self.checkButtonVar.append(tk.IntVar())
            self.letterCheckbutton = ttk.Checkbutton(frame, text=word[i], variable=self.checkButtonVar[i])
            self.letterCheckbutton.pack(side='left', ipadx=20, padx=30)

        frame.grid(column=0, row=1, ipadx=20, pady=5, sticky=tk.N)

        # buttons
        frame = ttk.Frame(self)

        self.playButton = ttk.Button(frame, text='Play Recording')
        self.playButton['command'] = self.playButtonClicked
        self.playButton.pack(side='left', ipadx=20, padx=30)

        self.submitButton = ttk.Button(frame, text='Submit')
        self.submitButton['command'] = self.submitButtonClicked
        self.submitButton.pack(side='right', ipadx=20, padx=30)

        frame.grid(column=0, row=2, ipadx=5, pady=5, sticky=tk.N)

    def playButtonClicked(self):

        in_data, mw = sf.read(self.recordingFileName)
        sd.wait()

        data = sd.play(in_data, mw)
        #sd.wait()

    def submitButtonClicked(self):
        self.destroy()

    def getResults(self):

        results = {}

        for i in range(0, len(self.word)):
            results[self.word[i]] = self.checkButtonVar[i]

        return results

class status(tk.Tk):

    def __init__(self, filename):

        if os.path.isfile(filename):
            self.record = pd.read_csv(filename)
        else:
          self.record['character'] = (list(string.ascii_uppercase))
          self.record['pass'] = 0
          self.record['fail'] = 0

        self.record.astype({'fail': 'float'}).dtypes
        self.record.astype({'pass': 'float'}).dtypes
        self.record['fail percentage'] = (self.record['fail']/(self.record['pass'] + self.record['fail'])) * 100

        self.record.sort_values('fail percentage', ascending=False, inplace=True)

    def plot(self):

        bar_colors = []
        for i in range (0, len(self.record)):
            if i < 10:
                bar_colors.append('r')
            else:
                bar_colors.append('g')

        self.record.plot(title='Morse Code Audio Character Recognition', x='character', y='fail percentage', kind='bar', color=bar_colors)
        plt.show()