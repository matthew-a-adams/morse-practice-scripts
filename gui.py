import os, string, time

import matplotlib.pyplot as plt
import pandas as pd
import sounddevice as sd
import soundfile as sf
import tkinter as tk

from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class tryoutApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # configure the root window
        self.title('Tryout App')

class appNotebook(ttk.Notebook):

    def __init__(self, container):
        super().__init__(container)

        self.pack(padx=10, pady=10, expand=True)

class appParameters(ttk.Frame):

    def __init__(self, container):
        super().__init__(container)

        self.__create_widgets()

        self.pack(padx=5, pady=5)

    def __create_widgets(self):

        sessionParms = sessionParameters(self)
        speedParms = speedParameters(self)
        characterParms = characterParameters(self)

class sessionParameters(ttk.LabelFrame):

    def __init__(self, container):
        super().__init__(container)

        self.config(text='Session')

        # setup the grid layout manager
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(0, weight=1)

        self.__create_widgets()

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def __create_widgets(self):

        # Number of phrases
        ttk.Label(self, text='Phrases').grid(column=1, row=0, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.phraseEntry = tk.Entry(self, width=3).grid(column=0, row=0, sticky=tk.W, padx=5)

        # Number of words per phrase
        ttk.Label(self, text='Words per Phrases').grid(column=1, row=1, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.wordEntry = tk.Entry(self, width=3).grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        # Number of characters per word
        ttk.Label(self, text='Characters per Word').grid(column=1, row=2, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.characterEntry = tk.Entry(self, width=3).grid(column=0, row=2, sticky=tk.W, padx=5)


class speedParameters(ttk.LabelFrame):

    def __init__(self, container):
        super().__init__(container)

        self.config(text='Speed')

        self.__create_widgets()

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def __create_widgets(self):

        # Number of phrases
        ttk.Label(self, text='Words per Minute (WPM)').grid(column=1,row=0, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.wpmEntry = tk.Entry(self, width=3).grid(column=0,row=0, sticky=tk.W, padx=5)

        # Number of words per phrase
        ttk.Label(self, text='Farnsworth Speed (FS)').grid(column=1,row=1, sticky=tk.W, ipadx=5, ipady=5, padx=5)
        self.fsEntry = tk.Entry(self, width=3).grid(column=0,row=1, sticky=tk.W, padx=5)

class characterParameters(ttk.LabelFrame):

    def __init__(self, container):
        super().__init__(container)

        self.config(text='Code Set')

        self.__create_widgets()

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

    def __create_widgets(self):

        characterSet = list(string.ascii_uppercase) + list(string.digits) + list('.?/,=')

        self.checkButtonVar = []

        # Character selection
        characterFrame = ttk.LabelFrame(self, text='Character')
        for i in range(0, len(characterSet)):
            self.checkButtonVar.append(tk.IntVar())
            self.letterCheckbutton = ttk.Checkbutton(characterFrame, text=characterSet[i], variable=self.checkButtonVar[i]).grid(column=i%10, row=int(i/10), sticky=tk.W, ipadx=5, ipady=5)
        #characterFrame.grid(column=0, row=0, ipadx=5, pady=5, sticky=tk.W, padx=5)
        characterFrame.pack(padx=5, pady=5, anchor='nw', fill='x')

        # Session selection
        lessonSet = ('Lesson 1', 'Lesson 2','Lesson 3','Lesson 4','Lesson 5','Lesson 6','Lesson 7','Lesson 8', 'Lesson 9', 'Lesson 10')

        lessonFrame = ttk.LabelFrame(self, text='CWOps Lessons')
        for j in range(i, i+len(lessonSet)):
            self.checkButtonVar.append(tk.IntVar())
            self.letterCheckbutton = ttk.Checkbutton(lessonFrame, text=lessonSet[j-i], variable=self.checkButtonVar[j]).grid(column=j%5, row=int(j/5), sticky = tk.W, ipadx = 5, ipady = 5)
        #LessonFrame.grid(column=0, row=1, ipadx=5, pady=5, sticky=tk.W, padx=5)
        lessonFrame.pack(padx=5, pady=5, anchor='nw', fill='x')

        # Lesson selection
        typeSet = ('letter', 'digit', 'punctuation')

        typeFrame = ttk.LabelFrame(self, text='Character Type')
        for j in range(i, i+len(typeSet)):
            self.checkButtonVar.append(tk.IntVar())
            self.letterCheckbutton = ttk.Checkbutton(typeFrame, text=typeSet[j-i], variable=self.checkButtonVar[j]).grid(column=j%5, row=int(j/5), sticky = tk.W, ipadx = 5, ipady = 5)
        #typeFrame.grid(column=0, row=2, ipadx=5, pady=5, sticky=tk.W, padx=5, columnspan=1)
        typeFrame.pack(padx=5, pady=5, anchor='nw', fill='x')

        # Selection buttons
        buttonFrame = ttk.Frame(self)
        allButton = ttk.Button(buttonFrame, text='Select All')
        allButton.grid(column=0, row=0, sticky = tk.N, ipadx = 5, ipady = 5, padx=5)
        noneButton = ttk.Button(buttonFrame, text='Select None')
        noneButton.grid(column=1, row=0, sticky = tk.N, ipadx = 5, ipady = 5, padx=5)
        #buttonFrame.grid(column=0, row=3, ipadx=5, pady=5, sticky=tk.W, padx=5)
        buttonFrame.pack(padx=5, pady=5, anchor='nw', fill='x')

class progressFrame(ttk.Frame):

    def __init__(self, container):
        super().__init__(container)

        self.__create_widgets()

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

        self.startTime = time.time()

    def __create_widgets(self):

        self.clock = ttk.Label(self, font = ('calibri', 40, 'bold'))
        self.clock.pack(anchor='center')

    def updateTime(self):

        float_time = round(time.time()-self.startTime)
        minutes, fraction = divmod(float_time * 60, 3600)  # split to hours and seconds
        seconds, fraction = divmod(fraction, 60)  # split the seconds to minutes and seconds
        text_input= "{:02.0f}:{:02.0f}".format(minutes, seconds)

        self.clock.config(text=text_input)
        self.clock.after(200, self.updateTime)

class graderFrame(ttk.Frame):

    def __init__(self, recordingName):

        self.words = [
            '111111111',
            '222222222',
            '333333333',
            '444444444',
            '555555555',
            '666666666',
            '777777777',
            '888888888',
            '999999999'
        ]

        super().__init__()

        self.checkButtonVar = []

        for r in range(0, len(self.words)):

            # Frame for one word
            frame = ttk.LabelFrame(self, text=self.words[r])

            # Play button for 1 word
            ttk.Button(frame, text='Play ' + self.words[r] + ' recording').pack(side='left', ipadx=5, padx=10, pady=10)

            # Checkboxes for tested letters
            for c in range(0, len(self.words[r])):
                self.checkButtonVar.append(tk.IntVar())
                self.letterCheckbutton = ttk.Checkbutton(frame, text=self.words[r][c], variable=self.checkButtonVar[c]).pack(side='left', ipadx=5, padx=5)

            frame.pack(padx=10, pady=10, anchor='nw', fill='x')


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
            if self.word[i] in results.keys():
                results[self.word[i]] += self.checkButtonVar[i].get()
            else:
                results[self.word[i]] = self.checkButtonVar[i].get()

        return results

class results(ttk.Frame):

    record = pd.DataFrame()

    def __init__(self, container, directory):

        super().__init__(container)

        if os.path.isdir(directory):
            for entry in os.scandir(directory):
                if entry.path.endswith('.csv') and entry.is_file():

                    df = pd.read_csv(entry.path)

                    if self.record.empty:
                        self.record = df
                    else:
                        self.record = pd.merge(self.record, df, on='character', suffixes=('_l','_r'))

                        self.record['pass'] = self.record['pass_l'] + self.record['pass_r']
                        self.record['fail'] = self.record['fail_l'] + self.record['fail_r']

                        self.record.astype({'fail_r': 'float'}).dtypes
                        self.record.astype({'pass_r': 'float'}).dtypes
                        self.record['last fail percentage'] = (self.record['fail_r'] / (self.record['pass_r'] + self.record['fail_r'])) * 100

                        self.record.drop(columns=['pass_l','pass_r','fail_l','fail_r'], inplace=True)

        self.record.astype({'fail': 'float'}).dtypes
        self.record.astype({'pass': 'float'}).dtypes
        self.record['fail percentage'] = (self.record['fail']/(self.record['pass'] + self.record['fail'])) * 100

        self.record.sort_values('fail percentage', ascending=False, inplace=True)

        df = self.record
        df.drop(columns=['pass', 'fail'], inplace=True)
        df.set_index('character', inplace=True)
        df.rename(columns={'fail percentage':'average', 'last fail percentage':'last run'}, inplace=True)

        barPlot = df.plot.bar(rot=0, color={'average':'blue', 'last run':'orange'}, title='Fail Percentage')
        #barPlot.set_facecolor('grey')

        graph = barPlot.get_figure()

        plot1 = FigureCanvasTkAgg(graph, self)
        plot1.get_tk_widget().grid(row=0,column=0,padx=30,pady=30)

        self.pack(padx=5, pady=5, anchor='nw', fill='x')

class status(tk.Tk):

    record = pd.DataFrame()

    def __init__(self, directory):

        if os.path.isdir(directory):
            for entry in os.scandir(directory):
                if entry.path.endswith('.csv') and entry.is_file():

                    df = pd.read_csv(entry.path)

                    if self.record.empty:
                        self.record = df
                    else:
                        self.record = pd.merge(self.record, df, how='outer', on='character', suffixes=('_l','_r'))

                        self.record.fillna(0, inplace=True)

                        self.record['pass'] = self.record['pass_l'] + self.record['pass_r']
                        self.record['fail'] = self.record['fail_l'] + self.record['fail_r']

                        self.record.astype({'fail_r': 'float'}).dtypes
                        self.record.astype({'pass_r': 'float'}).dtypes
                        self.record['last fail percentage'] = (self.record['fail_r'] / (self.record['pass_r'] + self.record['fail_r'])) * 100

                        self.record.drop(columns=['pass_l','pass_r','fail_l','fail_r'], inplace=True)

        self.record.astype({'fail': 'float'}).dtypes
        self.record.astype({'pass': 'float'}).dtypes
        self.record['fail percentage'] = (self.record['fail']/(self.record['pass'] + self.record['fail'])) * 100

        self.record.sort_values('fail percentage', ascending=False, inplace=True)

    def plot(self):

        # bar_colors = []
        # for i in range (0, len(self.record)):
        #     if i < 10:
        #         bar_colors.append('r')
        #     else:
        #         bar_colors.append('g')
        #
        # self.record.plot.bar(x='character', y='fail percentage', color=bar_colors)
        # self.record.plot.bar(rot=0, color=bar_colors)
        # plt.show()

        df = self.record
        df.drop(columns=['pass', 'fail'], inplace=True)
        df.set_index('character', inplace=True)
        df.rename(columns={'fail percentage':'average', 'last fail percentage':'last run'}, inplace=True)

        df.plot.bar(rot=0, color={'average':'blue', 'last run':'orange'}, title='Fail Percentage')
        plt.show()