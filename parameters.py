import format, speed, characters, start

import tkinter as tk
from tkinter import ttk

class Window(tk.Tk):

    def __init__(self):

        super().__init__()
        self.title('CWOps Basic Morse Practice Parameters')

        self.entries = {}

        self.format     = format.Frame(self)
        self.speed      = speed.Frame(self)
        self.characters = characters.Frame(self)

        tk.Button(self, text="Start", command=self.start, padx=5, pady=5).pack()

        self.mainloop()

    def start(self):
        self.retrieveEntries()
        self.destroy()

    def retrieveEntries(self):

        self.entries.update(self.format.getEntries())
        self.entries.update(self.speed.getEntries())
        self.entries.update(self.characters.getEntries())

    def getEntries(self):

        return self.entries
