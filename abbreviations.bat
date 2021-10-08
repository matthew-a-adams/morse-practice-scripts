@ECHO OFF
python "%~dp0\test.py" -i abbreviations.csv --wpm 25 --fs 4 --limit 10
@PAUSE