#!/usr/bin/env python3

from __future__ import division, print_function
import string, time, random, itertools, msvcrt, pyttsx3
import sounddevice as sd
import numpy as np
from scipy import io
import scipy.io.wavfile

from pydub import AudioSegment
import subprocess
import os
#from gtts import gTTS

import morse

SPS = 8000
LETTERS = string.ascii_uppercase
FREQ = 750
WPM = 25
FS = 10
AUDIO_PADDING = 0.5  # Seconds
CLICK_SMOOTH = 2  # Tone periods


def main(freq, wpm, fs, characters, limit, delay, obfuscate, prompt, outFile, inFile):

  if len(inFile) > 0:
    file_handle = open(inFile, 'r')
    messages = file_handle.readlines()
  else:
    messages = list(string.ascii_uppercase + string.digits + '.?,/=')
    if characters > 0:
      combinations = list(itertools.combinations(messages, characters))
      messages = []
      for combo in combinations:
        message = ''.join(combo)
        messages.append(message)

  if limit > 0:
    messages = random.choices(messages, k=limit)

  if prompt:
    # Load spoken letter WAV files
    letterNames = loadLetterNames()
    sps = letterNames[LETTERS[0]][0]
  else:
    sps = SPS
  print('Audio samples per second =', sps)
  print('Tone period     =', round(1000/freq, 1), 'ms')

  dps = morse.wpmToDps(wpm)  # Dots per second
  mspd = 1000/dps  # Dot duration in milliseconds
  farnsworthScale = morse.farnsworthScaleFactor(wpm, fs)
  print('Dot width       =', round(mspd, 1), 'ms')
  print('Dash width      =', int(round(mspd * morse.DASH_WIDTH)), 'ms')
  print('Character space =', int(round(mspd * morse.CHAR_SPACE * farnsworthScale)), 'ms')
  print('Word space      =', int(round(mspd * morse.WORD_SPACE * farnsworthScale)), 'ms')

  card_index = 1
  synthesizer = pyttsx3.init()

  for message in messages:

    print('Message =', message)

    # Chop newline character for file input
    if len(inFile) > 0:
      message = message[:-1]

    # Compute morse code audio from plain text
    #playMessage(message, sps, wpm, fs, freq)

    audio = stringToMorseAudio(message, sps, wpm, fs, freq, 0.5, None, promptVolume=0.3)
    audio /= 2
    io.wavfile.write('message.wav', sps, (audio * 2 ** 15).astype(np.int16))

    #Read the hi.wav file
    in_data, mv = sf.read('message.wav')
    sd.wait()

    print("GO!")

    #Start recording (wave_length Record for seconds. Wait until the recording is finished with wait)
    data = sd.playrec(in_data, mw, channels=1)
    sd.wait()

    #Normalize. Since it is recorded with 16 bits of quantization bit, it is maximized in the range of int16.
    data = data / data.max() * np.iinfo(np.int16).max

    # float -> int
    data = data.astype(np.int16)

    #Save file
    with wave.open(FILE_NAME, mode='wb') as wb:
        wb.setnchannels(1)  #monaural
        wb.setsampwidth(2)  # 16bit=2byte
        wb.setframerate(sample_rate)
        wb.writeframes(data.tobytes())  #Convert to byte string




def playMessage(message, sps, wpm, fs, freq):
  audio = stringToMorseAudio(message, sps, wpm, fs, freq, 0.5, None, promptVolume=0.3)
  audio /= 2

  playBlock(audio, sps)
  time.sleep(0.1)

def addAudio(base, new, offset):
  if base is None:
    base = np.array([], dtype=np.float32)
  assert offset >= 0
  lenBase, lenNew = len(base), len(new)
  if offset+lenNew > lenBase:
    # Make base longer by padding with zeros
    base = np.append(base, np.zeros(offset+lenNew-lenBase))
  base[offset:offset+lenNew] += new
  return base

def boolArrToSwitchedTone(boolArr, freq, sps, volume=1.0):
  ''' Create the tone audio from a bool array representation of morse code. '''
  weightLen = int(CLICK_SMOOTH*sps/freq)
  if weightLen % 2 == 0:
    weightLen += 1  # Make sure the weight array is odd length
  smoothingWeights = np.concatenate((np.arange(1, weightLen//2+1), np.arange(weightLen//2+1, 0, -1)))
  smoothingWeights = smoothingWeights / np.sum(smoothingWeights)
  numSamplesPadding = int(sps*AUDIO_PADDING) + int((weightLen-1)/2)
  padding = np.zeros(numSamplesPadding, dtype=bool)
  boolArr = np.concatenate((padding, boolArr, padding)).astype(np.float32)
  if CLICK_SMOOTH <= 0:
    smoothBoolArr = boolArr
  else:
    smoothBoolArr = np.correlate(boolArr, smoothingWeights, 'valid')
  numSamples = len(smoothBoolArr)
  x = np.arange(numSamples)
  toneArr = np.sin(x * (freq*2*np.pi/sps)) * volume
  toneArr *= smoothBoolArr
  return toneArr

def stringToMorseAudio(message, sps=SPS, wpm=WPM, fs=FS, freq=FREQ, volume=1.0, letterPrompts=None, promptVolume=1.0):
  message = message.upper()
  code = morse.stringToMorse(message)
  boolArr = morse.morseToBoolArr(code, sps, wpm, fs)
  audio = boolArrToSwitchedTone(boolArr, freq, sps, volume)
  numSamplesPadding = int(sps*AUDIO_PADDING)
  if letterPrompts is not None:
    for i in range(len(message)):
      l = message[i]
      if l in letterPrompts:
        offsetPlus = morse.morseSampleDuration(morse.stringToMorse(message[:i+1]), sps, wpm, fs)
        letterDuration = morse.morseSampleDuration(morse.letterToMorse(message[i]), sps, wpm, fs)
        offset = numSamplesPadding + offsetPlus - letterDuration
        audio = addAudio(audio, letterPrompts[l][1]*promptVolume, offset)
  return audio


def loadLetterNames(pathTemplate='audio/letter-names/%s_.wav', letters=LETTERS):
  out = {}
  for letter in letters:
    fName = pathTemplate % letter
    out[letter] = loadWav(fName)
  return out
def loadWav(fName):
  rate, data = io.wavfile.getHistory(fName, mmap=True)
  dataScale = data.astype(np.float32) / maxDtypeVolume(data.dtype)
  return rate, dataScale
def maxDtypeVolume(dtype):
  try:
    return np.iinfo(dtype).max  # Integer data type
  except ValueError:
    return 1.0  # Float data type
def playLetterNamesBlock(letterNames):
  sps = letterNames[LETTERS[0]][0]
  letterNameList = [letterNames[l][1] for l in LETTERS]
  alphabetAudio = np.concatenate(letterNameList)
  playBlock(alphabetAudio, sps)

def genTone(frequency, duration, sps=SPS, volume=1.0):
  return np.sin(np.arange(sps*duration)*(frequency*2*np.pi/sps))*volume
def playTone(*args, **kwargs):
  play(genTone(*args, **kwargs))
def play(array, sps=SPS):
  sd.play(array.astype(np.float32), sps)
def waitFor(array, sps=SPS):
  duration = len(array) / sps
  time.sleep(duration)
def playBlock(array, sps=SPS):
  play(array, sps)
  waitFor(array, sps)


if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code to audio flashcard.')
  parser.add_argument('-f', type=float, default=FREQ, help='Tone frequency')
  parser.add_argument('--wpm', type=float, default=WPM, help='Words per minute')
  parser.add_argument('--fs', type=float, default=FS, help='Farnsworth speed')
  parser.add_argument('--characters', type=int, default='0', help='Number of random characters in a card')
  parser.add_argument('--limit', type=int, default='0', help='The maximum number of cards to generate')
  parser.add_argument('--delay', type=float, default=5, help='Delay time between code and spoken answer')
  parser.add_argument('--obfuscate', action='store_true', default=False, help='Do not use message for flashcard file name')
  parser.add_argument('-p', action='store_true', default=False, help='Say letters along with morse code')
  parser.add_argument('-o', type=str, default='', help='Output to given WAV file instead of playing sound')
  parser.add_argument('-i', type=str, default='', help='Input from text file')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.characters, args.limit, args.delay, args.obfuscate, args.p, args.o, args.i)

