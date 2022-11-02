@ECHO OFF
python "%~dp0\..\..\audio_flashcard_generator.py" -i Word_ --delay 2 --wpm 20 --fs 20 --obfuscate
@PAUSE