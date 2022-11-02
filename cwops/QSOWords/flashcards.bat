@ECHO OFF
python "%~dp0\..\..\audio_flashcard_generator.py" -i QSO_ --delay 2 --wpm 10 --fs 5 --obfuscate
@PAUSE