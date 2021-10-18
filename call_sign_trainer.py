#!/usr/bin/env python3

from __future__ import division, print_function
import string, time, random, msvcrt
import sounddevice as sd
import numpy as np
from scipy import io
import scipy.io.wavfile

import morse

SPS = 8000
LETTERS = string.ascii_uppercase
FREQ = 750
WPM = 25
FS = 10
AUDIO_PADDING = 0.5  # Seconds
CLICK_SMOOTH = 2  # Tone periods

def main(freq, wpm, fs, limit, sign_type, us_origin, repeat, prompt, outFile):

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

  messages = []

  if type == '':
    prefix_character_count = random.choice([1, 3])
    suffix_character_count = random.choice([0, 3])
  else:
    prefix_character_count = int(sign_type[0])
    suffix_character_count = int(sign_type[-1]) - 1
    print("Generating " + str(prefix_character_count) + 'x' + str(suffix_character_count + 1) + ' call signs.')

  for i in range(0, limit):

    if us_origin:
      if prefix_character_count == 1:
        prefix = ''.join(random.choice(['K', 'N', 'W']))
      else:
        prefix = ''.join(random.choice(['A', 'K', 'N', 'W']) + random.choice(list(string.ascii_uppercase)))
      suffix = ''.join(random.choices(list(string.ascii_uppercase), k = suffix_character_count+1))
    else:
      prefix = ''.join(random.choices(list(string.ascii_uppercase + string.digits), k = prefix_character_count))
      suffix = ''.join(random.choices(list(string.ascii_uppercase + string.digits), k = suffix_character_count)) +  random.choice(list(string.ascii_uppercase))

    messages.append(prefix + random.choice(list(string.digits)) + suffix)

  testMessages(messages, repeat, sps, wpm, fs, freq)

def testMessages(messages, repeat, sps, wpm, fs, freq):

  random.shuffle(messages)

  # Keep track of failed messages and retest until all have been correctly tested.
  continue_with_test = True

  while continue_with_test:

    missed_count = 0
    continue_with_test = False
    retest_messages = []

    for message in messages:

      # Compute and play morse code audio from plain text
      if repeat:
        repeat_message = message + ' ' + message
        playMessage(repeat_message, sps, wpm, fs, freq)
      else :
        playMessage(message, sps, wpm, fs, freq)

      print('Enter message:')
      start = time.time()
      check = input()

      if check.upper() == message.upper():
        end = time.time()
        print('Correct! [', '{:.2f}'.format(end - start), 's]')
      else:
        print('Wrong. The correct answer is ', message)
        retest_messages.append(message)
        continue_with_test = True
        missed_count = missed_count + 1

    print('You missed ', missed_count, '. Retesting missed letters...')
    messages = retest_messages


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
  rate, data = io.wavfile.read(fName, mmap=True)
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

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('-f', type=float, default=FREQ, help='Tone frequency')
  parser.add_argument('--wpm', type=float, default=WPM, help='Words per minute')
  parser.add_argument('--fs', type=float, default=FS, help='Farnsworth speed')
  parser.add_argument('--limit', type=int, default=1, help='Limit to X queries')
  parser.add_argument('--type', type=str, default='', help='Call sign type, i.e. 1x3, 2x1, 2x3')
  parser.add_argument('--us', action='store_true', default=True, help='Caller origin either US or international')
  parser.add_argument('--repeat', action='store_true', default=True, help='Play the call sign code twice')
  parser.add_argument('-p', action='store_true', default=False, help='Say letters along with morse code')
  parser.add_argument('-o', type=str, default='', help='Output to given WAV file instead of playing sound')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.limit, args.type, args.us, args.repeat, args.p, args.o)

