@echo off
rem Opens the Farm Oasis Site Manager (needs Python 3 with Tkinter, which the
rem standard python.org installer includes).
cd /d "%~dp0"
where pythonw >nul 2>nul && (start "" pythonw "Site Manager.pyw" & exit /b)
where python >nul 2>nul && (start "" python "Site Manager.pyw" & exit /b)
where py >nul 2>nul && (start "" py -3 "Site Manager.pyw" & exit /b)
echo Python 3 was not found. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
pause
