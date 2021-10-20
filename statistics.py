class Statistics:

    def __init__(self):
        self.characters = dict()

    def record(self, character, time):
        self.characters.setdefault(character, []).append(time)

    def average(self, character):
        times = self.characters
        return sum(times) / len(times)

    def save(self):
        f = open('statisics.log', "a")

        for character in self.characters
            entry = character
            entry = entry + ' : ' +
        f.write("Now the file has more content!")
        f.close()
