import random, characters

class Phrase:

  def __init__(self, wordsPerPhrase = 0, charactersPerWord = 0, characterSet = characters.ALL):
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
        phrase.append(Word(self.charactersPerWord, self.characterSet).random())

    return phrase

class Word:

  def __init__(self, charactersPerWord=0, characterSet=characters.ALL):
    self.characterSet = characterSet
    self.charactersPerWord = charactersPerWord

  def random(self):

    if self.charactersPerWord == 0:
      length = random.randrange(1, 9)
    else:
      length = self.charactersPerWord

    return random.choices(self.characterSet, k=length)


