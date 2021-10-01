@ECHO OFF
python "%~dp0\..\..\audio_flashcard_generator.py" -i 0 --delay 3 --wpm 23 --fs 4 --obfuscate
@PAUSE