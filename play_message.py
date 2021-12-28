#!/usr/bin/env python3

from __future__ import division, print_function
import string, time
import sounddevice as sd
import numpy as np
from scipy import io
import scipy.io.wavfile

import morse

class Audio:

  sps = 8000
  letters = string.ascii_uppercase
  freq = 750
  wpm = 25
  fs = 10
  audio_padding = 0.5  # Seconds
  click_smooth = 2  # Tone periods

  word_space = 0.5 # Seconds

  def __init__(self, freq = 750, wpm = 25, fs = 10):
    self.freq = freq
    self.wpm = wpm
    self.fs = fs

    print('Audio samples per second =', self.sps)
    print('Tone period     =', round(1000 / self.freq, 1), 'ms')

    dps = morse.wpmToDps(self.wpm)  # Dots per second
    mspd = 1000 / dps  # Dot duration in milliseconds
    farnsworthScale = morse.farnsworthScaleFactor(self.wpm)
    print('Dot width       =', round(mspd, 1), 'ms')
    print('Dash width      =', int(round(mspd * morse.DASH_WIDTH)), 'ms')
    print('Character space =', int(round(mspd * morse.CHAR_SPACE * farnsworthScale)), 'ms')

    self.word_space = int(round(mspd * morse.WORD_SPACE * farnsworthScale))
    print('Word space      =', self.word_space, 'ms (', float(self.word_space/1000), 's)')

  def play(self, message):

    # Compute morse code audio from plain text
    audio = self.stringToMorseAudio(message, 0.5)
    audio /= 2

    self.playBlock(audio)
    time.sleep(0.1)

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
    code = morse.stringToMorse(message)
    boolArr = morse.morseToBoolArr(code, self.sps, self.wpm, self.fs)
    audio = self.boolArrToSwitchedTone(boolArr, volume)
    numSamplesPadding = int(self.sps*self.audio_padding)
    if letterPrompts is not None:
      for i in range(len(message)):
        l = message[i]
        if l in letterPrompts:
          offsetPlus = morse.morseSampleDuration(morse.stringToMorse(message[:i+1]), self.sps, self.wpm, self.fs)
          letterDuration = morse.morseSampleDuration(morse.letterToMorse(message[i]), self.sps, self.wpm, self.fs)
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
