@echo off
REM Discovery Tool v1.0
REM Finds: Claude Code, AI tools, config files, auth tokens
REM Runs on any Windows machine - outputs standard format
REM Usage: Run this file, copy results to your team

setlocal enabledelayedexpansion

set OUTPUT_FILE=discovery_results_%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%.txt

echo === DISCOVERY TOOL v1.0 === > %OUTPUT_FILE%
echo Machine: %COMPUTERNAME% >> %OUTPUT_FILE%
echo User: %USERNAME% >> %OUTPUT_FILE%
echo Date: %date% %time% >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

echo === CLAUDE CODE LOCATIONS === >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

for %%P in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Claude Code"
    "C:\Program Files\Claude Code"
    "C:\Program Files (x86)\Claude Code"
) do (
    echo Checking: %%P >> %OUTPUT_FILE%
    if exist %%P (
        echo STATUS: FOUND >> %OUTPUT_FILE%
        dir "%%P" /s /b 2>nul >> %OUTPUT_FILE%
    ) else (
        echo STATUS: NOT FOUND >> %OUTPUT_FILE%
    )
    echo. >> %OUTPUT_FILE%
)

echo === CONFIG & ENV FILES === >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

for %%F in (.env, .env.local, claude.env, config.json, settings.json) do (
    echo Searching for: %%F >> %OUTPUT_FILE%
    dir /s "C:\Users\%USERNAME%\%%F" 2>nul >> %OUTPUT_FILE%
    echo. >> %OUTPUT_FILE%
)

echo === OPENCLAW FOLDER === >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

if exist "C:\Users\%USERNAME%\.openclaw" (
    echo STATUS: FOUND >> %OUTPUT_FILE%
    dir "C:\Users\%USERNAME%\.openclaw" /s /b >> %OUTPUT_FILE%
) else (
    echo STATUS: NOT FOUND >> %OUTPUT_FILE%
)
echo. >> %OUTPUT_FILE%

echo === APPDATA FOLDERS === >> %OUTPUT_FILE%
echo. >> %OUTPUT_FILE%

if exist "C:\Users\%USERNAME%\AppData\Roaming\Claude" (
    echo Claude AppData folder found >> %OUTPUT_FILE%
    dir "C:\Users\%USERNAME%\AppData\Roaming\Claude" /s /b >> %OUTPUT_FILE%
) else (
    echo Claude AppData folder NOT found >> %OUTPUT_FILE%
)

echo. >> %OUTPUT_FILE%
echo === END DISCOVERY === >> %OUTPUT_FILE%
echo Results saved to: %OUTPUT_FILE% >> %OUTPUT_FILE%

echo.
echo Results saved to: %OUTPUT_FILE%
echo Opening file now...
start %OUTPUT_FILE%
