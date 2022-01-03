#!/usr/bin/env python3

from __future__ import division, print_function
import string, time
import sounddevice as sd
import numpy as np
from scipy import io
import scipy.io.wavfile

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

import morse, gui

def main(freq, wpm, fs, charactersPerWord, wordsPerPhrase, phrasesPerSession):

  audio = morse.audio(freq, wpm, fs)

  characters = morse.message(charactersPerWord, wordsPerPhrase).generate()

  for character in characters:
    audio.play(character, recordMic = True)

  grader = morse.grader()

  grader.checkPhraseAudio(characters)

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('-f', type=int, default=750, help='Tone frequency')
  parser.add_argument('--wpm', type=int, default=25, help='Words per minute')
  parser.add_argument('--fs', type=int, default=5, help='Farnsworth speed')
  parser.add_argument('--characters', type=int, default=1, help='Number of characters per word')
  parser.add_argument('--words', type=int, default=1, help='Number of words per phrase')
  parser.add_argument('--phrases', type=int, default=1, help='Number of phrases to generate')
  args = parser.parse_args()

  main(args.f, args.wpm, args.fs, args.characters, args.words, args.phrases)

