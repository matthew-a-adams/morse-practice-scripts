import tkinter as tk
from tkinter import ttk

WORDS = (
    '123456789',
    '0ABCDEFGH',
    'IJKLMNOPQ',
    'RSTUVWXYZ',
    '/=,?.*&#$',
    '123456789',
    '0ABCDEFGH',
    'IJKLMNOPQ',
    'RSTUVWXYZ'
)


class Checker(ttk.LabelFrame):

    def __init__(self, container, word):

        super().__init__(container, text=word)

        self.entries = []

        tk.Button(self, text="Play Recording", command=self.play).grid(column=0, row=1, sticky=tk.N, padx=5, pady=1)

        entryNumber = 1
        for character in list(word):
            self.entries.append(tk.StringVar(container))
            ttk.Label(self, text=character).grid(column=entryNumber, row=0, sticky=tk.S, padx=2, pady=1)
            tk.Entry(self, width=3, textvariable=self.entries[entryNumber-1]).grid(column=entryNumber, row=1, sticky=tk.N, ipadx=3, ipady=3, padx=2, pady=1)
            entryNumber = entryNumber + 1


        self.pack(ipadx=5, ipady=5, padx=5, pady=5, anchor='nw', fill='x')

    def play(self):
        print("Play audio here!")

class Frame(ttk.Frame):

    def __init__(self, container, words):

        super().__init__(container)

        self.checkers = {}

        for word in words:
            self.checkers[word] = Checker(self, word)

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

class Window(tk.Tk):

    def __init__(self):

        super().__init__()
        self.title('CWOps Basic Morse Practice Grader')

        self.frame = Frame(self, WORDS)

        self.mainloop()
