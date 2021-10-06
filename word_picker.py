from collections import Counter

with open('dictionary.txt') as fin:
    lines = (word.strip().upper() for word in fin)
    words = [(word, Counter(word)) for word in lines]

rack = Counter('ETANSIORHDLUCWMFYPGBVKJXQZ')
for scrabble_word, letter_count in words:
    # Using length here to limit output for example purposes
    if len(scrabble_word) <= 3 and not (letter_count - rack):
        print(scrabble_word)