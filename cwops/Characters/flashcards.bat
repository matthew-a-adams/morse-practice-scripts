@ECHO OFF
python "%~dp0\..\..\audio_flashcard_generator.py" -i 0 --delay 1 --wpm 15 --fs 15 --obfuscate
@PAUSE