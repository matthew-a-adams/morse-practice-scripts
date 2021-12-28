#!/usr/bin/env python3

from __future__ import division, print_function
import string, time, random, msvcrt
import sounddevice as sd
import soundfile as sf
import numpy as np
import wave
from scipy import io
import scipy.io.wavfile
import csv
from collections import Counter
import os
import speech_recognition as sr
import morse
import msvcrt

SPS = 8000
LETTERS = string.ascii_uppercase
FREQ = 750
WPM = 25
FS = 10
AUDIO_PADDING = 0.5  # Seconds
CLICK_SMOOTH = 2  # Tone periods

def main(freq, wpm, fs, prompt, force, phrases, time_out, length, outFile, inFile):

  messages = wordFinder(phrases, length)

  print('Message =', messages)

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

  print()
  print("Hit <ENTER> to start.")
  input()

  continue_with_test = True

  start_time = time.time()

  while continue_with_test:

    missed_count = 0
    continue_with_test = False
    retest_messages = []

    for message in messages:

      # Compute morse code audio from plain text
      playMessage(message, sps, wpm, fs, freq)

      check = recognizeRecording()
      # Print the message for verification
      if check.upper() == message.upper():
        print('Correct! Recognized: ' + check)
      else:
        if check == '-':
          print('The correct answer is ' + message)
        else:
          print('The correct answer is ' + message + '.  I heard ' + check + '.')

        # Play the user recording for verification
        print('Do you want me to play you recording? (Y/N)')
        if ord(msvcrt.getch()) == ord('y'):
          playRecording()

        # Confirm answer
        print('Was your answer correct? (Y/N)')
        if  ord(msvcrt.getch()) == ord('n'):
          retest_messages.append(message)
          continue_with_test = True
          missed_count = missed_count + 1

      if (time_out > 0) & ((time.time() - start_time) > time_out):
        print ("Times up!")
        exit()

    print('You missed ', missed_count, '. ')

    if force:
      print('Retesting missed message...')
      message = retest_messages
    elif time_out > 0:
        messages = wordFinder(phrases, length)

def wordFinder(limit, length):

  messages = []

  with open('dictionary.txt') as fin:
    lines = (word.strip().upper() for word in fin)
    words = [(word, Counter(word)) for word in lines]

  rack = Counter(''.join(list(string.ascii_uppercase)))

  for training_word, letter_count in words:

    # Using length here to limit output for example purposes
    if len(training_word) == length and not (letter_count - rack):
      messages.append(training_word)

  random.shuffle(messages)
  messages = random.choices(messages, k=limit)

  return messages

def playMessage(message, sps, wpm, fs, freq):

  message = message + ' '

  audio = stringToMorseAudio(message, sps, wpm, fs, freq, 0.5, None, promptVolume=0.3)
  audio /= 2
  io.wavfile.write('message.wav', sps, (audio * 2 ** 15).astype(np.int16))

  # Read the hi.wav file
  in_data, mw = sf.read('message.wav')
  sd.wait()

  # Start recording (wave_length Record for seconds. Wait until the recording is finished with wait)
  data = sd.playrec(in_data, mw, channels=1)
  sd.wait()

  if os.path.isfile('record.wav'):
    os.remove('record.wav')

  data /= 2
  io.wavfile.write('record.wav', sps, (data * 2 ** 15).astype(np.int16))

def recognizeRecording():
  r = sr.Recognizer()

  spelling = sr.AudioFile('record.wav')
  with spelling as source:
    audio = r.record(source)

  text = '-'

  try:
    text = r.recognize_google(audio)
  except sr.RequestError:
    # API was unreachable or unresponsive
    print('API unavailable.')
  except sr.UnknownValueError:
  # speech was unintelligible
    print('Unable to recognize speech.')

  text = text.upper()
  text = text.replace(" ", "")

  return text

def playRecording():

  # Read the hi.wav file
  in_data, mw = sf.read('record.wav')
  sd.wait()

  # Play the user recording
  data = sd.play(in_data, mw)
  sd.wait()

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
  print('Recording your answer...' )

  data = sd.playrec(array.astype(np.float32), sps, channels=2)

  # Normalize. Since it is recorded with 16 bits of quantization bit, it is maximized in the range of int16.
  data = data / data.max() * np.iinfo(np.int16).max

  # float -> int
  data = data.astype(np.int16)

  sample_rate = 16_000  # Sampling frequency

  # Save file
  with wave.open('./record.wav', mode='wb') as wb:
    wb.setnchannels(1)  # monaural
    wb.setsampwidth(2)  # 16bit=2byte
    wb.setframerate(sample_rate)
    wb.writeframes(data.tobytes())  # Convert to byte string

def waitFor(array, sps=SPS):
  duration = len(array) / sps
  time.sleep(duration)
def playBlock(array, sps=SPS):
  play(array, sps)
  waitFor(array, sps)

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('-f', type=float, default=FREQ, help='Tone frequency')
  parser.add_argument('--wpm', type=float, default=WPM, help='Words per minute')
  parser.add_argument('--fs', type=float, default=FS, help='Farnsworth speed')
  parser.add_argument('-p', action='store_true', default=False, help='Say letters along with morse code')
  parser.add_argument('--force', action='store_true', default=False, help='Force user to get the answer correct before completing')
  parser.add_argument('--phrases', type=int, default=10, help='Limit to as many phrases')
  parser.add_argument('--time', type=int, default=0, help='Limit practice time to as many seconds')
  parser.add_argument('--length', type=int, default=0, help='Length of the word')
  parser.add_argument('-o', type=str, default='', help='Output to given WAV file instead of playing sound')
  parser.add_argument('-i', type=str, default='', help='Input from text file')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.p, args.force, args.phrases, args.time, args.length, args.o, args.i)

