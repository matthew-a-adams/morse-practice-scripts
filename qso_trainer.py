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

class Person:
  def __init__(self, sign, name, location, rig, pwr, ant):
    self.sign = sign
    self.name = name
    self.location = location
    self.rig = rig
    self.pwr = pwr
    self.ant = ant
    self.rst = str(random.randrange(1,5)) + str(random.randrange(1,9)) + str(random.randrange(1,9))

def main(freq, wpm, fs, force, outFile, inFile):

  call_signs = []

  # Read from file in file provided
  #if len(inFile) > 0:
  #  file_handle = open(inFile, 'r')
  #  lines = file_handle.readlines()
  #  for line in lines:
  #    call_signs.append(line[:-1])
  #else:
  #  call_signs = ['KD2WAI', 'KO4HMB', 'KD2HCU', 'N1PRR', 'W8OV']
  operator = []

  operator.append(Person('KD2WAI', 'MATT', 'SCHNECTADY, NY',      'IC7300',      '100W', 'EFHW'))
  operator.append(Person('KO4HMB', 'DAVE', 'DANVILLE, VA',        'FT991A',      '5W',   'HAMSTICK'))
  operator.append(Person('KD2HCU', 'ERIC', 'YAPSHANK, NY',        'YEASU 817',   '50W',  'DIPOLE'))
  operator.append(Person('N1PRR',  'GARY', 'LITCHFIELD PARK, AZ', 'IC705',       '50W',  'SOTA'))
  operator.append(Person('W8OV',   'DAVE', 'COLLIN, TX',          'ELECRAFT K3', '100W', 'W RADIALS'))

  sps = SPS

  print('Audio samples per second =', sps)
  print('Tone period     =', round(1000/freq, 1), 'ms')

  dps = morse.wpmToDps(wpm)  # Dots per second
  mspd = 1000/dps  # Dot duration in milliseconds
  farnsworthScale = morse.farnsworthScaleFactor(wpm, fs)

  print()
  print('Dot width       =', round(mspd, 1), 'ms')
  print('Dash width      =', int(round(mspd * morse.DASH_WIDTH)), 'ms')
  print('Character space =', int(round(mspd * morse.CHAR_SPACE * farnsworthScale)), 'ms')
  print('Word space      =', int(round(mspd * morse.WORD_SPACE * farnsworthScale)), 'ms')

  print()
  print("Hit <ENTER> to start.")
  input()

  caller, callee = random.choices(operator, k=2)

  # CALLER

  # Is this frequency in use...
  playAndCheckMessage('QRL? QRL?', sps, wpm, fs, freq)
  playAndCheckMessage(random.choice(['QRL', 'A', 'L', 'Y', 'YES', '']), sps, wpm, fs, freq)

  # Request contact
  playAndCheckMessage('CQ CQ CQ DE ' + caller.sign + ' ' +caller.sign + ' K', sps, wpm, fs, freq)


  # CALLEE

  # Respond to CQ
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign + ' ' + callee.sign + ' K', sps, wpm, fs, freq)


  # CALLER

  # Response confirmation
  playAndCheckMessage(callee.sign + ' DE ' + caller.sign + ' BT', sps, wpm, fs, freq)

  # Request slower speed
  playAndCheckMessage(random.choice(['QRS', 'QRS PLS', 'QRS PSE', '']), sps, wpm, fs, freq)

  # Send thanks for the call
  playAndCheckMessage(random.choice(['GM ', 'GA ', 'GE ', '']) + 'THX ' + random.choice(['FOR ', 'FER ', '']) + 'CALL BT', sps, wpm, fs, freq)

  # Signal report
  playAndCheckMessage('UR RST IS '+ callee.rst + ' ' + callee.rst, sps, wpm, fs, freq)

  # Location
  playAndCheckMessage(random.choice(['IN ', 'QTH ']) + caller.location + ' ' + caller.location, sps, wpm, fs, freq)

  # Name
  playAndCheckMessage('NAME IS ' + caller.name + ' ' + caller.name, sps, wpm, fs, freq)

  # Back to callee
  playAndCheckMessage(random.choice(['BTU', 'HW CPY?']), sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(callee.sign + ' DE ' + caller.sign + ' K', sps, wpm, fs, freq)


  # CALLEE

  # Confirmation info
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign +  K', sps, wpm, fs, freq)

  # Signal report
  playAndCheckMessage('THX UR RST IS '+ caller.rst + ' ' + caller.rst, sps, wpm, fs, freq)

  # Location
  playAndCheckMessage(random.choice(['IN ', 'QTH ']) + callee.location + ' ' + callee.location, sps, wpm, fs, freq)

  # Name
  playAndCheckMessage('NAME IS ' + callee.name + ' ' + callee.name, sps, wpm, fs, freq)

  # Back to caller
  playAndCheckMessage(random.choice(['BTU', 'HW CPY?']), sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign + ' K', sps, wpm, fs, freq)


  # CALLER

  # Confirmation info
  playAndCheckMessage(callee.sign + ' DE ' + caller.sign, sps, wpm, fs, freq)

  # Send thanks for info
  playAndCheckMessage(random.choice(['THX ', 'THANKS ']) + random.choice(['FOR ', 'FER ', '']) + 'INFO BT',  sps, wpm, fs, freq)

  # Rig info
  playAndCheckMessage('RIG ' + random.choice(['HERE ', 'HR ', ''])  + 'IS ' + caller.rig + ' AT ' + caller.pwr + 'W BT', sps, wpm, fs, freq)

  # Antenna
  playAndCheckMessage('ANT IS ' + caller.ant + ' BT', sps, wpm, fs, freq)

  # Back to callee
  playAndCheckMessage(random.choice(['BTU', 'HW CPY?']), sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(callee.sign + ' DE ' + caller.sign + ' K', sps, wpm, fs, freq)

  # CALLEE

  # Confirmation info
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign, sps, wpm, fs, freq)

  # Send thanks for info
  playAndCheckMessage(random.choice(['THX ', 'THANKS ']) + random.choice(['FOR ', 'FER ', '']) + 'INFO BT',  sps, wpm, fs, freq)

  # Rig info
  playAndCheckMessage('RIG ' + random.choice(['HERE ', 'HR ', ''])  + 'IS ' + callee.rig + ' AT ' + callee.pwr + 'W BT', sps, wpm, fs, freq)

  # Antenna
  playAndCheckMessage('ANT IS ' + callee.ant + ' BT', sps, wpm, fs, freq)

  # Back to caller
  playAndCheckMessage(random.choice(['BTU', 'HW CPY?']), sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign + ' K', sps, wpm, fs, freq)


  # CALLER

  # Send thanks for info
  playAndCheckMessage(random.choice(['THX ', 'THANKS ']) + random.choice(['FOR ', 'FER ', '']) + 'QSO ' + callee.name + ' ES 73',  sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(callee.sign + ' DE ' + caller.sign + ' SK', sps, wpm, fs, freq)


  # CALLEE

  # Send thanks for info
  playAndCheckMessage(random.choice(['THX ', 'THANKS ']) + random.choice(['FOR ', 'FER ', '']) + 'QSO ' + caller.name + ' ES 73',  sps, wpm, fs, freq)

  # Confirmation info
  playAndCheckMessage(caller.sign + ' DE ' + callee.sign + ' SK', sps, wpm, fs, freq)

def playAndCheckMessage(message, sps, wpm, fs, freq):

  if message == '':
    return

  playMessage(message, sps, wpm, fs, freq)

  print('Enter message:')
  start = time.time()
  check = input()

  if check.upper() == message.upper():
    end = time.time()
    print('Correct! [', '{:.2f}'.format(end - start), 's]')
  else:
    print('Wrong. The correct answer is ', message)

  print("Hit <ENTER> to continue.")
  input()

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
  parser.add_argument('--force', action='store_true', default=False, help='Force user to get the answer correct before completing')
  parser.add_argument('-o', type=str, default='', help='Output to given WAV file instead of playing sound')
  parser.add_argument('-i', type=str, default='', help='Input from text file')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.force, args.o, args.i)

