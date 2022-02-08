@ECHO OFF
"%~dp0.\python38\python.exe" "%~dp0.\src\ScrapeTikTokComments.py"

FOR /F "DELIMS=#" %%E IN ('"PROMPT #$E# & FOR %%E IN (1) DO REM"') DO (SET "\E=%%E")
ECHO %\e%[32m[*]%\e%[0m Press any key to close.
>NUL PAUSE
>NUL PAUSE
