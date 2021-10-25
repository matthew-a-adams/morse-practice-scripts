import os.path
import numpy as np
import pandas as pd

class CharacterStatistics:

    characters = pd.DataFrame()

    def __init__(self):
        self.characters = pd.DataFrame()

    def recordTime(self, character, time):
        if self.characters.empty:
            self.characters = pd.DataFrame({character : [time]})
        else:
            new = pd.DataFrame({character : [time]})
            self.characters = pd.concat([self.characters, new], axis=1)

    def getAverageTime(self, character):
        return self.characters[character].mean()

    def getAverageTimes(self):
        return self.characters.mean().round(3)

    def exist(self):
        if self.characters.empty:
            return False
        else:
            return True

    def merge(self, other, inplace=False):
        other.characters = pd.concat([other.characters, self.characters])

        if inplace:
            self.characters = other.characters

        return other

    def show(self):
        this = self.getAverageTimes()
        historical = self.getHistory().getAverageTimes()

        df = this

        if historical.empty == False:

            df = pd.concat([this, historical], axis=1)

            df[0] = df[0].map('[{:,.3f} s]'.format)
            df[1] = df[1].map('[{:,.3f} s]'.format)
            df[2] = np.where(df[0] <= df[1], '\u2193', '\u2191')

            df = df.rename(columns={0 : 'Current', 1 : 'Average', 2 : ''})

        #df.iloc[1].plot.bar()

        print(df.to_string())

    def save(self):
        self.characters = self.characters.round(3)
        self.characters.to_csv('statistics.csv', float_format='%.3f', index=False)

    def update(self):
        self.characters = self.characters.round(3)
        self.merge(self.getHistory(), inplace=True)
        self.characters.to_csv('statistics.csv', float_format='%.3f', index=False)

    def getHistory(self):
        history = CharacterStatistics()

        if os.path.exists('statistics.csv'):
            history.characters = pd.read_csv('statistics.csv')

        return history
