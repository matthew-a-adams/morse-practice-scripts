import speech_recognition as sr

r = sr.Recognizer()

spelling = sr.AudioFile('record.wav')
with spelling as source:
    audio = r.record(source)

print(r.recognize_google(audio))

