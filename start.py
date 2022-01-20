import tkinter as tk
from tkinter import ttk

class Button(ttk.Button):

    def __init__(self, container):

        super().__init__(container)

        tk.Button(container, text ="Start", command = self.start, padx=5, pady=5).pack()

    def start(self):
        self.master.retrieve()
        print(self.master.get())
        self.master.destroy()