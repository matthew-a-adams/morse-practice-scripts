import string

import tkinter as tk
from tkinter import ttk

CHARACTER_TYPE = {
              'Characters'  : list(string.ascii_uppercase),
              'Digits'      : list(string.digits),
              'Punctuation' : list('.?,/=')
}

CWOPS_SESSION_CHARACTERS = {
              'Session 1'  : list('ETAN'),
              'Session 2'  : list('OSI14'),
              'Session 3'  : list('RHDL25'),
              'Session 4'  : list('UC.'),
              'Session 5'  : list('MW36?'),
              'Session 6'  : list('FY'),
              'Session 7'  : list('PG79/'),
              'Session 8'  : list('BV='),
              'Session 9'  : list('KJ80'),
              'Session 10' : list('XQZ'),

}

ALL = CHARACTER_TYPE['Characters'] + CHARACTER_TYPE['Digits'] + CHARACTER_TYPE['Punctuation']

class SelectionSet:

    def __init__(self, container, label, width, selectionSet):

        self.entries = {}
        self.container = container

        for selection in selectionSet:
            self.entries[selection] = tk.BooleanVar(container, True)

        self.frame = ttk.LabelFrame(container, text=label)

        entryNumber = 0
        for entry in self.entries:
            ttk.Checkbutton(self.frame, text=entry, variable=self.entries[entry], command=self.respondToSelection).grid(column=entryNumber % width, row=int(entryNumber / width), sticky=tk.W, ipadx=5, ipady=5)
            entryNumber = entryNumber + 1

        self.frame.pack(padx=5, pady=5, anchor='nw', fill='x')

    def setSelection(self, selectionSet, value = True):

        for selection in selectionSet:
            self.entries[selection].set(value)

    def getSelection(self):

        selection = ''

        for entry in self.entries:
            if self.entries[entry].get():
                selection = selection + entry

        return selection

    def respondToSelection(self):

        if self.frame.cget('text') == 'Type':
            for type in CHARACTER_TYPE:
                self.container.characters.set(CHARACTER_TYPE[type], self.entries[type].get())

        if self.frame.cget('text') == 'CWOPs Beginner Sessions':
            for session in CWOPS_SESSION_CHARACTERS:
                self.container.characters.set(CWOPS_SESSION_CHARACTERS[session], self.entries[session].get())

        self.syncSelection()

    def syncSelection(self):

        characterSet = self.container.characters.get()

        for session in CWOPS_SESSION_CHARACTERS:
            self.container.sessions.set([session], (set(CWOPS_SESSION_CHARACTERS[session]) & set(characterSet)) == set(CWOPS_SESSION_CHARACTERS[session]))

        for type in CHARACTER_TYPE:
            self.container.types.set([type], (set(CHARACTER_TYPE[type]) & set(characterSet)) == set(CHARACTER_TYPE[type]))

class SelectionButtons:

    def __init__(self, container):

        self.container = container

        frame = ttk.Frame(container)

        tk.Button(frame, text=" Select Entire Test Set ", command=self.selectAll  ).grid(row = 0, column = 1, padx=5, pady=5)
        tk.Button(frame, text="Deselect Entire Test Set", command=self.deselectAll).grid(row = 0, column = 2, padx=5, pady=5)

        frame.pack(padx=5, pady=5, fill='x')

    def selectAll(self):
        self.container.characters.set(ALL, True)
        self.container.characters.sync()

    def deselectAll(self):
        self.container.characters.set(ALL, False)
        self.container.characters.sync()

class Frame(ttk.LabelFrame):

    def __init__(self, container, initialCharacterSet = ALL, initialSessionSet = CWOPS_SESSION_CHARACTERS.keys(), initialTypeSet = CHARACTER_TYPE.keys()):
        super().__init__(container, text='Test Set')

        self.characters = SelectionSet(self, 'Characters',              10, initialCharacterSet)
        self.sessions   = SelectionSet(self, 'CWOPs Beginner Sessions',  5,  initialSessionSet)
        self.types      = SelectionSet(self, 'Type',                    10, initialTypeSet)

        self.buttons = SelectionButtons(self)

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def getEntries(self):
        entries = {}

        entries['Characters'] = self.characters.getSelection()

        return entries