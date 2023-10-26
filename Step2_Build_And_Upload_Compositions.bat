@echo off
python "%~dp0%\main.py" -buildAndUploadCompositions Rem /? 

Rem Kommentar
Rem IF NOT %ERRORLEVEL%==9009 ECHO "Tool finished. Find the generated files in 'ManualTasks' or 'Output' Directory"

Rem IF %ERRORLEVEL%==9009 ECHO python.exe was not found on PATH. 
Rem IF %ERRORLEVEL%==9009 ECHO Add python to PATH or substitute the correct path to python.exe in this .bat-file.

pause > NUL