@echo off
REM YouTube Video Downloader - Render Deployment Verification Script
REM This script checks if all required files are present for Render deployment

echo.
echo ================================================
echo  Render Deployment Verification
echo ================================================
echo.

setlocal enabledelayedexpansion
set "missing=0"

REM Check for required files
echo Checking for required files...
echo.

if exist "Procfile" (
    echo [OK] Procfile found
) else (
    echo [ERROR] Procfile NOT found - REQUIRED!
    set missing=1
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt NOT found - REQUIRED!
    set missing=1
)

if exist "backend\app.py" (
    echo [OK] backend\app.py found
) else (
    echo [ERROR] backend\app.py NOT found - REQUIRED!
    set missing=1
)

if exist "frontend\index.html" (
    echo [OK] frontend\index.html found
) else (
    echo [ERROR] frontend\index.html NOT found - REQUIRED!
    set missing=1
)

if exist ".gitignore" (
    echo [OK] .gitignore found
) else (
    echo [WARNING] .gitignore NOT found
)

if exist "README.md" (
    echo [OK] README.md found
) else (
    echo [WARNING] README.md NOT found
)

echo.
echo Checking dependencies in requirements.txt...
echo.

REM Check if gunicorn is in requirements.txt
findstr /I "gunicorn" requirements.txt > nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] gunicorn found in requirements.txt
) else (
    echo [WARNING] gunicorn NOT in requirements.txt - REQUIRED for Render!
    set missing=1
)

REM Check if flask is in requirements.txt
findstr /I "flask" requirements.txt > nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] flask found in requirements.txt
) else (
    echo [WARNING] flask NOT in requirements.txt - REQUIRED!
    set missing=1
)

REM Check if yt-dlp is in requirements.txt
findstr /I "yt-dlp\|yt_dlp" requirements.txt > nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] yt-dlp found in requirements.txt
) else (
    echo [WARNING] yt-dlp NOT in requirements.txt - REQUIRED!
    set missing=1
)

echo.
echo Checking Procfile contents...
echo.

REM Check Procfile content
findstr /I "gunicorn" Procfile > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Procfile contains gunicorn command
) else (
    echo [ERROR] Procfile does not contain gunicorn - FIX REQUIRED!
    set missing=1
)

echo.
echo ================================================
echo  Deployment Guides Available:
echo ================================================
echo.

if exist "STEP_BY_STEP.md" (
    echo [OK] STEP_BY_STEP.md - Start here first!
) else (
    echo [INFO] STEP_BY_STEP.md - Not found
)

if exist "RENDER_SIMPLE.md" (
    echo [OK] RENDER_SIMPLE.md - Simplified guide
) else (
    echo [INFO] RENDER_SIMPLE.md - Not found
)

if exist "GIT_SETUP.md" (
    echo [OK] GIT_SETUP.md - If new to Git
) else (
    echo [INFO] GIT_SETUP.md - Not found
)

if exist "DEPLOYMENT_CHECKLIST.md" (
    echo [OK] DEPLOYMENT_CHECKLIST.md - Pre-deployment check
) else (
    echo [INFO] DEPLOYMENT_CHECKLIST.md - Not found
)

if exist "DEPLOY_TO_RENDER.md" (
    echo [OK] DEPLOY_TO_RENDER.md - Master guide
) else (
    echo [INFO] DEPLOY_TO_RENDER.md - Not found
)

echo.
echo ================================================
echo  Verification Results
echo ================================================
echo.

if %missing% EQU 0 (
    echo [SUCCESS] All required files are present!
    echo.
    echo You can now:
    echo 1. Push code to GitHub (see GIT_SETUP.md)
    echo 2. Deploy to Render (see RENDER_SIMPLE.md)
    echo 3. Share your app with the world!
    echo.
    echo First-time? Read STEP_BY_STEP.md
    echo.
) else (
    echo [ERROR] Some required files are missing!
    echo.
    echo Fix the errors above before deploying.
    echo.
    echo Need help? Check DEPLOYMENT_CHECKLIST.md
    echo.
)

pause
