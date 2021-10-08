@ECHO OFF
python "%~dp0\..\..\audio_flashcard_generator.py" -i 0 --delay 2 --wpm 25 --fs 25 --obfuscate
@PAUSE