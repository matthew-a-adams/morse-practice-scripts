@ECHO OFF
python "%~dp0\call_sign_trainer.py" --repeat --limit 10 --type 1x2 --wpm 27 --fs 4 --us
@PAUSE