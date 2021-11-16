@echo off
python "%~dp0%\main.py" /?  2> NUL

Rem Kommentar
IF NOT %ERRORLEVEL%==9009 ECHO "Tool finished. Find the generated files in 'ManualTasks' or 'Output' Directory"

IF %ERRORLEVEL%==9009 ECHO python.exe was not found on PATH. 
IF %ERRORLEVEL%==9009 ECHO Add python to PATH or substitute the correct path to python.exe in this .bat-file.

pause > NUL