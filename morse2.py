import configparser, os, random, string, time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

import numpy as np
import pandas as pd
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import io
import scipy.io.wavfile

from morseTable import forwardTable, DOT, DASH, DASH_WIDTH, CHAR_SPACE, WORD_SPACE

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

ALL_CHARACTERS = CHARACTER_TYPE['Characters'] + CHARACTER_TYPE['Digits'] + CHARACTER_TYPE['Punctuation']

class Parameters(tk.Tk):

    class Format(ttk.LabelFrame):

        class LabeledEntry:

            def __init__(self, container, label, number, initialValue=1):
                self.value = tk.StringVar(value=initialValue)
                ttk.Label(container, text=label).grid(column=1, row=number, sticky=tk.W, ipadx=5, ipady=5, padx=5)
                self.phraseEntry = tk.Entry(container, width=3, textvariable=self.value).grid(column=0, row=number, sticky=tk.W, padx=5)

            def get(self):
                return int(self.value.get())

            def set(self, value):
                self.value.set(value)

        def __init__(self, container, initialWordsPerPhrase=1, initialCharactersPerWord=1):
            super().__init__(container, text='Format')

            self.wordsPerPhrase = self.LabeledEntry(self, 'Words Per Session', 1, initialWordsPerPhrase)
            self.charactersPerWord = self.LabeledEntry(self, 'Characters Per Word', 2, initialCharactersPerWord)

            self.pack(padx=5, pady=5, anchor='nw', fill='x')

        def get(self):
            entries = {}

            # entries['NumberOfPhrases']   = self.numberOfPhrases.getEntry()
            entries['WordsPerPhrase'] = self.wordsPerPhrase.get()
            entries['CharactersPerWord'] = self.wordsPerPhrase.get()

            return entries

        def set(self, wordsPerPhrase, charactersPerWord):
            self.wordsPerPhrase.set(wordsPerPhrase)
            self.wordsPerPhrase.set(charactersPerWord)

    class Speed(ttk.LabelFrame):

        class LabeledEntry:

            def __init__(self, container, label, number, initialValue=1):
                self.value = tk.StringVar(value=initialValue)
                ttk.Label(container, text=label).grid(column=1, row=number, sticky=tk.W, ipadx=5, ipady=5, padx=5)
                self.phraseEntry = tk.Entry(container, width=3, textvariable=self.value).grid(column=0, row=number, sticky=tk.W, padx=5)

            def get(self):
                return self.value.get()

            def set(self, value):
                self.value.set(value)

        def __init__(self, container, initialWordsPerMinute=25, initialFarnsworthSpeed=4):
            super().__init__(container, text='Speed')

            self.wordsPerMinute = self.LabeledEntry(self, 'Words per Minute (WPM)', 0, initialWordsPerMinute)
            self.farnsworthSpeed = self.LabeledEntry(self, 'Farnsworth Speed (FS)', 1, initialFarnsworthSpeed)

            self.pack(padx=5, pady=5, anchor='nw', fill='x')

        def get(self):
            entries = {}

            entries['WordsPerMinute'] = self.wordsPerMinute.get()
            entries['FarnsworthSpeed'] = self.farnsworthSpeed.get()

            return entries

        def set(self, wordsPerMinute, farnsworthSpeed):
            self.wordsPerMinute.set(wordsPerMinute)
            self.farnsworthSpeed.set(farnsworthSpeed)

    class Characters(ttk.LabelFrame):

        class SelectionSet:

            def __init__(self, container, label, width, selectionSet):

                self.entries = {}
                self.container = container

                for selection in selectionSet:
                    self.entries[selection] = tk.BooleanVar(container, True)

                self.frame = ttk.LabelFrame(container, text=label)

                entryNumber = 0
                for entry in self.entries:
                    ttk.Checkbutton(self.frame, text=entry, variable=self.entries[entry], command=self.respond).grid(column=entryNumber % width, row=int(entryNumber / width), sticky=tk.W, ipadx=5, ipady=5)
                    entryNumber = entryNumber + 1

                self.frame.pack(padx=5, pady=5, anchor='nw', fill='x')

            def set(self, selectionSet, value=True):

                for selection in selectionSet:
                    self.entries[selection].set(value)

            def get(self):

                selection = ''

                for entry in self.entries:
                    if self.entries[entry].get():
                        selection = selection + entry

                return selection

            def respond(self):

                if self.frame.cget('text') == 'Type':
                    for type in CHARACTER_TYPE:
                        self.container.characters.set(CHARACTER_TYPE[type], self.entries[type].get())

                if self.frame.cget('text') == 'CWOPs Beginner Sessions':
                    for session in CWOPS_SESSION_CHARACTERS:
                        self.container.characters.set(CWOPS_SESSION_CHARACTERS[session], self.entries[session].get())

                self.sync()

            def sync(self):

                characterSet = self.container.characters.get()

                for session in CWOPS_SESSION_CHARACTERS:
                    self.container.sessions.set([session], (set(CWOPS_SESSION_CHARACTERS[session]) & set(characterSet)) == set(CWOPS_SESSION_CHARACTERS[session]))

                for type in CHARACTER_TYPE:
                    self.container.types.set([type], (set(CHARACTER_TYPE[type]) & set(characterSet)) == set(CHARACTER_TYPE[type]))

        class SelectionButtons:

            def __init__(self, container):
                self.container = container

                frame = ttk.Frame(container)

                tk.Button(frame, text=" Select Entire Test Set ", command=self.selectAll).grid(row=0, column=1, padx=5, pady=5)
                tk.Button(frame, text="Deselect Entire Test Set", command=self.deselectAll).grid(row=0, column=2, padx=5, pady=5)

                frame.pack(padx=5, pady=5, fill='x')

            def selectAll(self):
                self.container.characters.set(ALL_CHARACTERS, True)
                self.container.characters.sync()

            def deselectAll(self):
                self.container.characters.set(ALL_CHARACTERS, False)
                self.container.characters.sync()

        def __init__(self, container, initialCharacterSet=ALL_CHARACTERS):
            super().__init__(container, text='Test Set')

            self.characters = self.SelectionSet(self, 'Characters', 10, ALL_CHARACTERS)
            self.sessions = self.SelectionSet(self, 'CWOPs Beginner Sessions', 5, CWOPS_SESSION_CHARACTERS.keys())
            self.types = self.SelectionSet(self, 'Type', 10, CHARACTER_TYPE.keys())

            self.buttons = self.SelectionButtons(self)

            # Select requested characters
            self.buttons.deselectAll()
            self.characters.set(initialCharacterSet)
            self.characters.sync()

            self.pack(padx=5, pady=5, anchor='nw', fill='x')

        def get(self):
            entries = {}

            entries['Set'] = self.characters.get()

            return entries

        def set(self, selectionSet):
            self.characters.set(ALL_CHARACTERS, False)
            self.characters.set(selectionSet)
            self.characters.sync()

    class Config(ttk.LabelFrame):

        def __init__(self, container):

            super().__init__(container, text='Using Last Configuration')

            frame = ttk.Frame(self)

            tk.Button(frame, text="Load Configuration", command=self.load).grid(row=0, column=1, padx=5, pady=5)
            tk.Button(frame, text="Save Configuration", command=self.save).grid(row=0, column=2, padx=5, pady=5)

            frame.pack(padx=5, pady=5, fill='x')

            self.pack(padx=5, pady=5, anchor='nw', fill='x')

        def load(self):
            filename = fd.askopenfilename(filetypes = [('Config', '*.ini')], defaultextension = [('Config', '*.ini')])
            self.master.load(filename)
            self.master.set()

            name = os.path.basename(filename)
            name = os.path.splitext(name)[0]
            self.master.configuration.configure(text = 'Using ' + name + ' Configuration')

        def save(self):
            filename = fd.asksaveasfilename(filetypes = [('Config', '*.ini')], defaultextension = [('Config', '*.ini')])
            self.master.save(filename)

            name = os.path.basename(filename)
            name = os.path.splitext(name)[0]
            self.master.configuration.configure(text = 'Using ' + name + ' Configuration')

    def __init__(self):

        super().__init__()
        self.title('CWOps Basic Morse Practice Parameters')

        self.entries = {}

        # Read from config file
        self.load('last.ini')

        # Create the interface
        self.format = self.Format(self, self.config['Format']['WordsPerPhrase'], self.config['Format']['CharactersPerWord'])
        self.speed  = self.Speed(self, self.config['Speed']['WordsPerMinute'], self.config['Speed']['FarnsworthSpeed'])
        self.characters = self.Characters(self, self.config['Characters']['Set'])
        self.configuration = self.Config(self)

        tk.Button(self, text="Start", command=self.start, padx=5, pady=5).pack()

        self.mainloop()

    def start(self):
        # Save setting to the ini file
        self.save('last.ini')

        # Close the interface
        self.destroy()

    def get(self):
        return self.entries

    def set(self):
        self.format.set(self.config['Format']['WordsPerPhrase'], self.config['Format']['CharactersPerWord'])
        self.speed.set(self.config['Speed']['WordsPerMinute'], self.config['Speed']['FarnsworthSpeed'])
        self.characters.set(self.config['Characters']['Set'])

    def load(self, filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

    def save(self, filename):
        self.config = configparser.ConfigParser()

        # Pull information from the interface
        self.entries['Format'] = self.format.get()
        self.entries['Speed'] = self.speed.get()
        self.entries['Characters'] = self.characters.get()

        # Convert entries to config file info
        for type in self.entries:
            self.config[type] = self.entries[type]

        with open(filename, 'w') as configfile:
            self.config.write(configfile)

class Phrase:

    class Word:

        def __init__(self, charactersPerWord = 0, characterSet = ALL_CHARACTERS):
            self.characterSet = characterSet
            self.charactersPerWord = charactersPerWord

        def random(self):

            if self.charactersPerWord == 0:
                length = random.randrange(1, 9)
            else:
                length = self.charactersPerWord

            return ''.join(random.choices(self.characterSet, k=length))

    def __init__(self, wordsPerPhrase = 0, charactersPerWord = 0, characterSet = ALL_CHARACTERS):
        self.wordsPerPhrase = wordsPerPhrase
        self.charactersPerWord = charactersPerWord
        self.characterSet =  characterSet

    def random(self):
        phrase = []

        if self.wordsPerPhrase == 0:
          length = random.randrange(1, 9)
        else:
          length = self.wordsPerPhrase

        for word in range(0, length):
            phrase.append(self.Word(self.charactersPerWord, self.characterSet).random())

        return phrase

class Audio:

  sps = 8000
  letters = string.ascii_uppercase
  freq = 750
  wpm = 25
  fs = 10
  audio_padding = 0.5  # Seconds
  click_smooth = 2  # Tone periods

  word_space = 0.5 # Seconds

  entry = 1

  def __init__(self, freq = 750, wpm = 25, fs = 10):

    self.freq = float(freq)
    self.wpm = float(wpm)
    self.fs = float(fs)

    #print('Audio samples per second =', self.sps)
    #print('Tone period     =', round(1000 / self.freq, 1), 'ms')

    dps = wpmToDps(self.wpm)  # Dots per second
    mspd = 1000 / dps  # Dot duration in milliseconds
    farnsworthScale = farnsworthScaleFactor(self.wpm)
    #print('Dot width       =', round(mspd, 1), 'ms')
    #print('Dash width      =', int(round(mspd * DASH_WIDTH)), 'ms')
    #print('Character space =', int(round(mspd * CHAR_SPACE * farnsworthScale)), 'ms')

    self.word_space = int(round(mspd * WORD_SPACE * farnsworthScale/4))
    #print('Word space      =', self.word_space, 'ms (', float(self.word_space/1000), 's)')

  def play(self, message, recordMic = False):

    # Add padding to record audio
    if recordMic:
      audioMessage = message + ' '

    # Compute morse code audio from plain text
    audio = self.stringToMorseAudio(audioMessage + ' ', 0.5)
    audio /= 2

    if recordMic:
      self.playAndRecordBlock(audio, message)
    else:
      self.playBlock(audio)

  def space(self):
    time.sleep(float(self.word_space/1000))

  def addAudio(self, base, new, offset):
    if base is None:
      base = np.array([], dtype=np.float32)
    assert offset >= 0
    lenBase, lenNew = len(base), len(new)
    if offset+lenNew > lenBase:
      # Make base longer by padding with zeros
      base = np.append(base, np.zeros(offset+lenNew-lenBase))
    base[offset:offset+lenNew] += new
    return base

  def boolArrToSwitchedTone(self, boolArr, volume=1.0):
    ''' Create the tone audio from a bool array representation of morse code. '''
    weightLen = int(self.click_smooth*self.sps/self.freq)
    if weightLen % 2 == 0:
      weightLen += 1  # Make sure the weight array is odd length
    smoothingWeights = np.concatenate((np.arange(1, weightLen//2+1), np.arange(weightLen//2+1, 0, -1)))
    smoothingWeights = smoothingWeights / np.sum(smoothingWeights)
    numSamplesPadding = int(self.sps*self.audio_padding) + int((weightLen-1)/2)
    padding = np.zeros(numSamplesPadding, dtype=bool)
    boolArr = np.concatenate((padding, boolArr, padding)).astype(np.float32)
    if self.click_smooth <= 0:
      smoothBoolArr = boolArr
    else:
      smoothBoolArr = np.correlate(boolArr, smoothingWeights, 'valid')
    numSamples = len(smoothBoolArr)
    x = np.arange(numSamples)
    toneArr = np.sin(x * (self.freq*2*np.pi/self.sps)) * volume
    toneArr *= smoothBoolArr
    return toneArr

  def stringToMorseAudio(self, message, volume=1.0, letterPrompts=None, promptVolume=1.0):
    message = message.upper()
    code = stringToMorse(message)
    boolArr = morseToBoolArr(code, self.sps, self.wpm, self.fs)
    audio = self.boolArrToSwitchedTone(boolArr, volume)
    numSamplesPadding = int(self.sps*self.audio_padding)
    if letterPrompts is not None:
      for i in range(len(message)):
        l = message[i]
        if l in letterPrompts:
          offsetPlus = morseSampleDuration(stringToMorse(message[:i+1]), self.sps, self.wpm, self.fs)
          letterDuration = morseSampleDuration(letterToMorse(message[i]), self.sps, self.wpm, self.fs)
          offset = numSamplesPadding + offsetPlus - letterDuration
          audio = self.addAudio(audio, letterPrompts[l][1]*promptVolume, offset)
    return audio

  def genTone(self, frequency, duration, volume=1.0):
    return np.sin(np.arange(self.sps*duration)*(frequency*2*np.pi/self.sps))*volume

  def playTone(self, *args, **kwargs):
    play(self.genTone(*args, **kwargs))

  def waitFor(self, array):
    duration = len(array) / self.sps
    time.sleep(duration)

  def playBlock(self, array):
    sd.play(array.astype(np.float32), self.sps)
    self.waitFor(array)

  def playAndRecordBlock(self, audio, message):
    io.wavfile.write('audio.wav', self.sps, (audio * 2 ** 15).astype(np.int16))

    in_data, mw = sf.read('audio.wav')
    sd.wait()

    os.remove('audio.wav')

    # Start recording (wave_length Record for seconds. Wait until the recording is finished with wait)
    data = sd.playrec(in_data, mw, channels=1)
    sd.wait()

    recording = message

    recording = recording.replace(',', 'comma')
    recording = recording.replace('!', 'exclimation')
    recording = recording.replace('?', 'question')
    recording = recording.replace('=', 'equal')
    recording = recording.replace('.', 'period')
    recording = recording.replace('/', 'slash')

    recording = recording + '.wav'

    data /= 2
    io.wavfile.write(recording, self.sps, (data * 2 ** 15).astype(np.int16))


def letterToMorse(letter):
    if letter in forwardTable:
        return forwardTable[letter]
    elif letter.isspace():
        return ' '
    else:
        return ''


def stringToMorse(string):
    codeArr = [letterToMorse(l) for l in string.upper()]
    trimmedArr = [code for code in codeArr if code]
    return ' '.join(trimmedArr)


def morseSampleDuration(code, sps, wpm, fs=None):
    dps = wpmToDps(wpm)  # dots per second
    baseSampleCount = sps / dps
    samplesPerDot = int(round(baseSampleCount))
    samplesPerDash = int(round(baseSampleCount * DASH_WIDTH))
    samplesBetweenElements = int(round(baseSampleCount))
    farnsworthScale = farnsworthScaleFactor(wpm, fs)
    samplesBetweenLetters = int(round(baseSampleCount * CHAR_SPACE * farnsworthScale))
    samplesBetweenWords = int(round(baseSampleCount * WORD_SPACE * farnsworthScale))

    dotArr = np.ones(samplesPerDot, dtype=np.bool)
    dashArr = np.ones(samplesPerDash, dtype=np.bool)
    eGapArr = np.zeros(samplesBetweenElements, dtype=np.bool)
    cGapArr = np.zeros(samplesBetweenLetters, dtype=np.bool)
    wGapArr = np.zeros(samplesBetweenWords, dtype=np.bool)

    duration = 0
    prevSpaces = 0
    prevWasElement = False
    for c in code:
        if (c == DOT or c == DASH) and prevWasElement:
            duration += samplesBetweenElements
        if c == DOT:
            duration += samplesPerDot
            prevSpaces, prevWasElement = 0, True
        elif c == DASH:
            duration += samplesPerDash
            prevSpaces, prevWasElement = 0, True
        else:  # Assume the char is a space otherwise
            if prevSpaces == 1:
                duration += samplesBetweenWords - samplesBetweenLetters
            elif prevSpaces == 0:
                duration += samplesBetweenLetters
            prevSpaces += 1
            prevWasElement = False

    return duration


def morseToBoolArr(code, sps, wpm, fs=None):
    dps = wpmToDps(wpm)  # dots per second
    baseSampleCount = sps / dps
    samplesPerDot = int(round(baseSampleCount))
    samplesPerDash = int(round(baseSampleCount * DASH_WIDTH))
    samplesBetweenElements = int(round(baseSampleCount))
    farnsworthScale = farnsworthScaleFactor(wpm, fs)
    samplesBetweenLetters = int(round(baseSampleCount * CHAR_SPACE * farnsworthScale))
    samplesBetweenWords = int(round(baseSampleCount * WORD_SPACE * farnsworthScale))

    dotArr = np.ones(samplesPerDot, dtype=np.bool)
    dashArr = np.ones(samplesPerDash, dtype=np.bool)
    eGapArr = np.zeros(samplesBetweenElements, dtype=np.bool)
    cGapArr = np.zeros(samplesBetweenLetters, dtype=np.bool)
    wGapArr = np.zeros(samplesBetweenWords, dtype=np.bool)

    pieces = []
    prevWasSpace = False
    prevWasElement = False
    for c in code:
        if (c == DOT or c == DASH) and prevWasElement:
            pieces.append(eGapArr)
        if c == DOT:
            pieces.append(dotArr)
            prevWasSpace, prevWasElement = False, True
        elif c == DASH:
            pieces.append(dashArr)
            prevWasSpace, prevWasElement = False, True
        else:  # Assume the char is a space otherwise
            if prevWasSpace:
                pieces[-1] = wGapArr
            else:
                pieces.append(cGapArr)
            prevWasSpace, prevWasElement = True, False

    return np.concatenate(pieces)


def wpmToDps(wpm):
    ''' Words per minute = number of times PARIS can be sent per minute.
        PARIS takes 50 dot lengths to send.  Returns dots per seconds. '''
    return wpm * 50 / 60.0


def farnsworthScaleFactor(wpm, fs=None):
    ''' Returns the multiple that character and word spacing should be multiplied by. '''
    if fs is None:
        return 1  # Standard (not Farnsworth) word spacing
    slowWordInterval = 1.0 / fs  # Minutes per word
    standardWordInterval = 1.0 / wpm
    extraSpace = slowWordInterval - standardWordInterval
    extraSpaceDots = (extraSpace / standardWordInterval) * (9 + 10 + 4 * DASH_WIDTH + 4 * CHAR_SPACE + WORD_SPACE)
    standardSpaceDots = 4 * CHAR_SPACE + WORD_SPACE  # For the word PARIS
    totalSpaceDots = standardSpaceDots + extraSpaceDots
    scaleFactor = totalSpaceDots / standardSpaceDots
    if scaleFactor < 1:
        return 1
    return scaleFactor

class Grader(tk.Tk):

    class Interface(ttk.Frame):

        class WordFrame(ttk.LabelFrame):

            class LabeledEntry:

                def __init__(self, container, character, column):
                    self.answer = tk.StringVar(container)
                    ttk.Label(container, text=character).grid(column=column, row=0, sticky=tk.S, padx=2, pady=1)
                    entry = tk.Entry(container, width=3, textvariable=self.answer).grid(column=column, row=1, sticky=tk.N, ipadx=3, ipady=3, padx=2, pady=1)
                    self.answer.trace("w", self.autocapitalize)

                def get(self):
                    return self.answer.get()

                def autocapitalize(self, *arg):
                    self.answer.set(self.answer.get().capitalize())

            def __init__(self, container, word):
                super().__init__(container, text=word)

                self.answer = word
                self.entry = []

                tk.Button(self, text="Play Recording", command=self.play).grid(column=0, row=1, sticky=tk.N, padx=5, pady=1)

                for index in range(0, len(word)):
                    self.entry.append(self.LabeledEntry(self, self.answer[index], index + 1))

                self.pack(ipadx=5, ipady=5, padx=5, pady=5, anchor='nw', fill='x')

            def play(self):

                recording = self.answer

                recording = recording.replace(',', 'comma')
                recording = recording.replace('!', 'exclimation')
                recording = recording.replace('?', 'question')
                recording = recording.replace('=', 'equal')
                recording = recording.replace('.', 'period')
                recording = recording.replace('/', 'slash')

                recording = recording + '.wav'

                in_data, mw = sf.read(recording)
                sd.wait()
                data = sd.play(in_data, mw)

            def grade(self):

                correct = {}
                wrong = {}
                deamons = []

                for character in self.answer:
                    correct[character] = 0
                    wrong[character] = 0

                for index in range(0, len(self.answer)):
                    if self.entry[index].get() == self.answer[index]:
                        correct[self.answer[index]] = correct[self.answer[index]] + 1
                    else:
                        wrong[self.answer[index]] = wrong[self.answer[index]] + 1
                        if str(self.entry[index].get()) != '':
                            deamons.append(str(self.answer[index]) + str(self.entry[index].get()))

                # Delete audio file after grading
                recording = self.answer

                recording = recording.replace(',', 'comma')
                recording = recording.replace('!', 'exclimation')
                recording = recording.replace('?', 'question')
                recording = recording.replace('=', 'equal')
                recording = recording.replace('.', 'period')
                recording = recording.replace('/', 'slash')

                recording = recording + '.wav'

                os.remove(recording)

                return (correct, wrong, deamons)

        def __init__(self, container, words):
            super().__init__(container)

            self.checkers = {}

            for word in words:
                self.checkers[word] = self.WordFrame(self, word)

            self.pack(padx=5, pady=5, anchor='nw', fill='x')

        def grade(self):

            correct= {}
            wrong = {}
            deamons = {}

            for word in self.checkers:
                correct[word], wrong[word], deamons[word] = self.checkers[word].grade()

            return (correct, wrong, deamons)

    def __init__(self, words):

        self.words = words

        super().__init__()
        self.title('CWOps Basic Morse Practice Grader')

        self.interface = self.Interface(self, words)
        tk.Button(self, text="Grade", command=self.grade, padx=5, pady=5).pack()

        self.mainloop()

    def grade(self, directory = 'temp'):

        correct, wrong, deamons = self.interface.grade()

        characterDF = pd.DataFrame()

        characterDF['character'] = (list(string.ascii_uppercase) + list(string.digits) + list('.?,/='))
        characterDF['pass'] = 0
        characterDF['fail'] = 0

        for word in correct:
            for character in correct[word]:
                index = characterDF.index[characterDF['character'] == character][0]
                characterDF.at[index, 'pass'] += correct[word][character]

        for word in wrong:
            for character in wrong[word]:
                index = characterDF.index[characterDF['character'] == character][0]
                characterDF.at[index, 'fail'] += wrong[word][character]

        time_string = time.strftime("%Y%m%d%H%M", time.localtime())
        filename = directory + '/' + time_string + '.csv'

        if not os.path.isdir(directory):
          os.mkdir(directory)

        characterDF.to_csv(filename, index=False)

        # Record deamons
        filename = 'deamons.csv'

        deamonDF = pd.DataFrame({'deamon': [], 'count': []})

        if os.path.exists(filename):
            deamonDF = pd.read_csv(filename)

        for word in deamons:
            for deamon in deamons[word]:
                if deamon in deamonDF.values:
                    index = deamonDF.index[deamonDF['deamon'] == deamon][0]
                    deamonDF.at[index, 'count'] += int(1)
                else:
                    deamonDF.loc[len(deamonDF.index)] = [deamon, int(1)]

            deamonDF.to_csv(filename, index=False)

            # Close the interface
            self.destroy()


class Performance(tk.Tk):

    characterDF = pd.DataFrame()
    sessionDF = pd.DataFrame()

    def __init__(self, directory = 'temp'):

        if os.path.isdir(directory):
            for entry in os.scandir(directory):
                if entry.path.endswith('.csv') and entry.is_file():

                    csvDF = pd.read_csv(entry.path)

                    # Calculate letter percentages
                    if self.characterDF.empty:
                        self.characterDF = csvDF
                    else:
                        self.characterDF = pd.merge(self.characterDF, csvDF, how='outer', on='character', suffixes=('_l', '_r'))

                        self.characterDF.fillna(0, inplace=True)

                        self.characterDF['pass'] = self.characterDF['pass_l'] + self.characterDF['pass_r']
                        self.characterDF['fail'] = self.characterDF['fail_l'] + self.characterDF['fail_r']

                        self.characterDF.astype({'fail_r': 'float'}).dtypes
                        self.characterDF.astype({'pass_r': 'float'}).dtypes

                        self.characterDF['last pass percentage'] = (self.characterDF['pass_r'] / (self.characterDF['pass_r'] + self.characterDF['fail_r'])) * 100

                        self.characterDF.drop(columns=['pass_l', 'pass_r', 'fail_l', 'fail_r'], inplace=True)

                    # Calculate session percentages
                    total_fails = csvDF['fail'].sum()
                    total_passes = csvDF['pass'].sum()
                    total_attempts = total_fails + total_passes
                    percent_correct = (total_passes / total_attempts) * 100

                    if self.sessionDF.empty:
                        self.sessionDF = pd.DataFrame([[entry.name, (csvDF['pass'].sum() / (csvDF['pass'].sum() + csvDF['fail'].sum())) * 100]], columns=['sessions', 'percentage'])
                    else:
                        self.sessionDF.loc[len(self.sessionDF.index)] = [entry.name, (csvDF['pass'].sum() / (csvDF['pass'].sum() + csvDF['fail'].sum())) * 100]

        self.characterDF.astype({'fail': 'float'}).dtypes
        self.characterDF.astype({'pass': 'float'}).dtypes
        self.characterDF['pass percentage'] = (self.characterDF['pass'] / (self.characterDF['pass'] + self.characterDF['fail'])) * 100

        self.characterDF.sort_values('pass percentage', ascending=False, inplace=True)

    def plot(self):

        # Plot character percentages
        tempDF = self.characterDF
        tempDF.drop(columns=['pass', 'fail'], inplace=True)
        tempDF.set_index('character', inplace=True)
        tempDF.rename(columns={'pass percentage':'average', 'last pass percentage':'last run'}, inplace=True)

        tempDF.plot.bar(rot=0, color={'average':'blue', 'last run':'orange'}, title='Percentage Correct')
        plt.show()

        # Plot session percentages
        tempDF = self.sessionDF
        tempDF.set_index('sessions', inplace=True)
        tempDF.plot.line(rot=0, color={'percentage':'blue'}, title='ICR Percentage')

        plt.gca().axes.get_xaxis().set_visible(False)
        plt.show()