#!/usr/bin/env python3

import os, random, string, time

import numpy as np
import pandas as pd
import sounddevice as sd
import soundfile as sf

from scipy import io

from morseTable import forwardTable, DOT, DASH, DASH_WIDTH, CHAR_SPACE, WORD_SPACE

import gui

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
  baseSampleCount = sps/dps
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
        duration += samplesBetweenWords-samplesBetweenLetters
      elif prevSpaces == 0:
        duration += samplesBetweenLetters
      prevSpaces += 1
      prevWasElement = False

  return duration

def morseToBoolArr(code, sps, wpm, fs=None):
  dps = wpmToDps(wpm)  # dots per second
  baseSampleCount = sps/dps
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
  return wpm*50/60.0

def farnsworthScaleFactor(wpm, fs=None):
  ''' Returns the multiple that character and word spacing should be multiplied by. '''
  if fs is None:
    return 1  # Standard (not Farnsworth) word spacing
  slowWordInterval = 1.0/fs  # Minutes per word
  standardWordInterval = 1.0/wpm
  extraSpace = slowWordInterval-standardWordInterval
  extraSpaceDots = (extraSpace/standardWordInterval) * (9+10+4*DASH_WIDTH+4*CHAR_SPACE+WORD_SPACE)
  standardSpaceDots = 4*CHAR_SPACE + WORD_SPACE  # For the word PARIS
  totalSpaceDots = standardSpaceDots + extraSpaceDots
  scaleFactor = totalSpaceDots / standardSpaceDots
  if scaleFactor < 1:
    return 1
  return scaleFactor


if __name__ == '__main__':
  import sys

  if len(sys.argv) >= 2:
    message = ' '.join(sys.argv[1:])
    print(stringToMorse(message))
  else:
    try:
      while True:
        message = input()
        print(stringToMorse(message))
    except EOFError:
      pass

class audio:

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
    self.freq = freq
    self.wpm = wpm
    self.fs = fs

    print('Audio samples per second =', self.sps)
    print('Tone period     =', round(1000 / self.freq, 1), 'ms')

    dps = wpmToDps(self.wpm)  # Dots per second
    mspd = 1000 / dps  # Dot duration in milliseconds
    farnsworthScale = farnsworthScaleFactor(self.wpm)
    print('Dot width       =', round(mspd, 1), 'ms')
    print('Dash width      =', int(round(mspd * DASH_WIDTH)), 'ms')
    print('Character space =', int(round(mspd * CHAR_SPACE * farnsworthScale)), 'ms')

    self.word_space = int(round(mspd * WORD_SPACE * farnsworthScale/4))
    print('Word space      =', self.word_space, 'ms (', float(self.word_space/1000), 's)')

  def play(self, message, recordMic = False):

    # Add padding to record audio
    if recordMic:
      message = message + ' '

    # Compute morse code audio from plain text
    audio = self.stringToMorseAudio(message, 0.5)
    audio /= 2

    if recordMic:
      self.playAndRecordBlock(audio)
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

  def playAndRecordBlock(self, audio):
    io.wavfile.write('audio.wav', self.sps, (audio * 2 ** 15).astype(np.int16))

    in_data, mw = sf.read('audio.wav')
    sd.wait()

    # Start recording (wave_length Record for seconds. Wait until the recording is finished with wait)
    data = sd.playrec(in_data, mw, channels=1)
    sd.wait()

    recording = str(self.entry) + '.wav'

    if os.path.isfile(recording):
      os.remove(recording)

    data /= 2
    io.wavfile.write(recording, self.sps, (data * 2 ** 15).astype(np.int16))

    self.entry = self.entry + 1

class message:

  alphabet = []

  numberOfWords = 1
  numberOfCharacters = 1

  def __init__(self, charactersPerWord=1, wordsPerPhrase=1, alphabet=list(string.digits) + list(string.ascii_uppercase) + list('.?,/=')):

    self.alphabet = alphabet
    self.numberOfWords = wordsPerPhrase
    self.numberOfCharacters = charactersPerWord

  def generateCharacter(self):
    return random.choices(self.alphabet, k=1)

  def generateWord(self, dictionary=[]):

    word = []
    word_str = ''

    for character in range(0, self.numberOfCharacters, 1):
      word += self.generateCharacter()

    return word_str.join(word)

  def generate(self):

    phrase = []

    for word in range(0, self.numberOfWords, 1):
      phrase.append(self.generateWord())


    return phrase

class grader:

  record = pd.DataFrame()

  def __init__(self, outputDirectory = 'scores'):

    self.record['character'] = (list(string.ascii_uppercase) + list(string.digits) + list('.?,/='))
    self.record['pass'] = 0
    self.record['fail'] = 0
    self.directory = outputDirectory


  def checkCharacterAudio(self, message):

    entry = 1

    for character in message:

      if character == ' ':
        entry = entry + 1
        continue

      print('The character is ', character, '. Does this match your recording? [y/n]')

      recording = str(entry) + '.wav'
      in_data, mw = sf.read(recording)
      sd.wait()

      data = sd.play(in_data, mw)
      sd.wait()

      check = input()

      index = self.record.index[self.record['character'] == character][0]

      if check == 'y':
        print('Great!')
        self.record.at[index, 'pass'] = self.record.at[index, 'pass'] + 1
      else:
        print('Too bad.')
        self.record.at[index, 'fail'] = self.record.at[index, 'fail'] + 1

      os.remove(recording)

      entry = entry + 1

    print(self.record)
    self.record.to_csv('record.csv', index=False)

  def checkPhraseAudio(self, message):

    entry = 1

    for word in message:

      test = gui.window(word, entry)
      test.mainloop()

      correct, wrong = test.getResults()

      for character in correct:
        index = self.record.index[self.record['character'] == character][0]
        self.record.at[index, 'pass'] += correct[character]

      for character in wrong:
        index = self.record.index[self.record['character'] == character][0]
        self.record.at[index, 'fail'] += wrong[character]

      entry = entry + 1

    time_string = time.strftime("%Y%m%d%H%M", time.localtime())
    filename = self.directory + '/' + time_string + '.csv'

    if not os.path.isdir(self.directory):
      os.mkdir(self.directory)

    self.record.to_csv(filename, index=False)

class alphabet:

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

    def array(self):
        return self.set
