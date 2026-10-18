@echo off
setlocal
rem Extracts exefs\main from a Metroid Dread update NSP using hactool.
rem Put this file, hactool.exe, prod.keys and the update .nsp in one folder,
rem then double-click it.
cd /d "%~dp0"

if not exist hactool.exe (echo [!] hactool.exe not found in %cd% & goto :fail)
if not exist prod.keys (echo [!] prod.keys not found in %cd% & goto :fail)

if not exist update\*.nca (
  set "NSP="
  for %%n in (*.nsp) do set "NSP=%%n"
  if not defined NSP (echo [!] No update folder and no .nsp file found & goto :fail)
)
if not exist update\*.nca (
  echo Unpacking %NSP% ...
  hactool -k prod.keys -t pfs0 --outdir=update "%NSP%" >nul 2>&1
)
if not exist update\*.tik (echo [!] No .tik file in the update folder & goto :fail)

set "KEY="
for /f "usebackq delims=" %%k in (`powershell -NoProfile -Command "$b=[IO.File]::ReadAllBytes((Get-ChildItem update\*.tik | Select-Object -First 1).FullName); -join ($b[0x180..0x18F] | ForEach-Object { $_.ToString('x2') })"`) do set "KEY=%%k"
if not defined KEY (echo [!] Could not read the title key & goto :fail)
echo Title key: %KEY%

set "PROG="
for %%f in (update\*.nca) do (
  hactool -k prod.keys "%%f" 2>nul | findstr /R /C:"Content Type:.*Program" >nul && set "PROG=%%f"
)
if not defined PROG (echo [!] Could not find the Program NCA & goto :fail)
echo Program NCA: %PROG%

if exist exefs rmdir /s /q exefs
hactool -k prod.keys --titlekey=%KEY% --exefsdir=exefs "%PROG%" >hactool_log.txt 2>&1

if exist exefs\main (
  echo.
  echo SUCCESS: %cd%\exefs\main
  dir exefs
  pause
  exit /b 0
)
echo [!] exefs\main was not created. Details are in hactool_log.txt

:fail
echo.
echo FAILED - copy this window's text into the chat.
pause
exit /b 1
