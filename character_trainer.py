#!/usr/bin/env python3

from __future__ import division, print_function
import string, time, random, msvcrt, itertools
import sounddevice as sd
import numpy as np
from scipy import io
import scipy.io.wavfile

import morse
import morseStatistics as ms

SPS = 8000
LETTERS = string.ascii_uppercase
FREQ = 750
WPM = 25
FS = 10
AUDIO_PADDING = 0.5  # Seconds
CLICK_SMOOTH = 2  # Tone periods

SESSIONS = [
              ['E', 'T', 'A', 'N'],             # Session 1
              ['O', 'S', 'I', '1', '4'],        # Session 2
              ['R', 'H', 'D', 'L', '2', '5'],   # Session 3
              ['U', 'C', '.' ],                 # Session 4
              ['M', 'W', '3', '6', '?'],        # Session 5
              ['F', 'Y', ','],                  # Session 6
              ['P', 'G', '7', '9', '/'],        # Session 7
              ['B', 'V', '='] ,                 # Session 8
              ['K', 'J', '8', '0'] ,            # Session 9
              ['X', 'Q', 'Z']                   # Session 10
]

STATS = ms.CharacterStatistics()

def main(freq, wpm, fs, limit, time_limit, quick, session, multiple, prompt, outFile):

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

  # Loop through all sets staring with the newest. After completing the newest sets and the next set to the newest
  # and retest. Continue to add the next newest set and retest until all the way through.
  if session == 0:
    session_sets = len(SESSIONS)
  else:
    session_sets = session

  if quick:
    messages = []
    for set in range(0, session_sets, 1):
      messages = messages + SESSIONS[set]

    testMessages(messages, limit, time_limit, multiple, sps, wpm, fs, freq)

  else:
    for group_end in range(session_sets-1, -1, -1):

      sets = [*range(session_sets, group_end, -1)]
      print('Group', session_sets - group_end, 'testing sessions', sets)

      messages = []
      for set in sets:
        messages = messages + SESSIONS[set - 1]

      testMessages(messages, limit, time_limit, multiple, sps, wpm, fs, freq)

  STATS.show()

  STATS.update()

def testMessages(messages, limit, time_limit, multiple, sps, wpm, fs, freq):

  random.shuffle(messages)

  if multiple > 1:
    multiple_messages = list(itertools.combinations(messages, multiple))

    messages = []
    for combo in multiple_messages:
      message = ''.join(combo)
      messages.append(message)

    if limit  > 0:
      messages = random.choices(messages, k=limit)
    else:
      messages = messages

  # Keep track of failed messages and retest until all have been correctly tested.
  continue_with_test = True

  while continue_with_test:

    missed_count = 0
    continue_with_test = False
    retest_messages = []

    for message in messages:

      # Compute morse code audio from plain text
      playMessage(message, sps, wpm, fs, freq)

      print('Enter message:')
      start_time = time.time()
      check = msvcrt.getch()

      print(chr(ord(check)).upper())

      match = ord(check) == ord(message.lower())

      response_time = time.time() - start_time
      timed_out = (time_limit > 0) and (time_limit > response_time)

      if timed_out:
        print('Time limit reached [', '{:.2f}'.format(response_time), 's]')
        retest_messages.append(message)
        continue_with_test = True
        missed_count = missed_count + 1
        #print('Hit <ENTER> to continue.')
        #input()
      elif match:
        print('Correct! [', '{:.2f}'.format(response_time), 's]')
        STATS.recordTime(chr(ord(check)).upper(), response_time)
      else:
        print('Wrong. The correct answer is ', chr(ord(message)))
        retest_messages.append(message)
        continue_with_test = True
        missed_count = missed_count + 1
        #print('Hit <ENTER> to continue.')
        #input()

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

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('-f', type=float, default=FREQ, help='Tone frequency')
  parser.add_argument('--wpm', type=float, default=WPM, help='Words per minute')
  parser.add_argument('--fs', type=float, default=FS, help='Farnsworth speed')
  parser.add_argument('--limit', type=int, default=0, help='Limit to X queries')
  parser.add_argument('--tl', type=float, default=0.0, help='Time limit (in seconds) before moving on the next character')
  parser.add_argument('--quick', action='store_true', default=False, help='Short test (once through each letter)')
  parser.add_argument('--session', type=int, default=0, help='CWA test session charcter set')
  parser.add_argument('--multiple', type=int, default=1, help='Number of random characters in a row (default = 1)')
  parser.add_argument('-p', action='store_true', default=False, help='Say letters along with morse code')
  parser.add_argument('-o', type=str, default='', help='Output to given WAV file instead of playing sound')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.limit, args.tl, args.quick, args.session, args.multiple, args.p, args.o)

