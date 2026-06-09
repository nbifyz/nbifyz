@echo off
chcp 65001 > nul
echo ============================================
echo Очистка старых сессий (>30 дней)
echo ============================================
echo.

set "SESSIONS_DIR=sessions"
set "ARCHIVE_DIR=%SESSIONS_DIR%\archive"
set "DAYS=30"

if not exist "%SESSIONS_DIR%" (
    echo Каталог сессий не найден: %SESSIONS_DIR%
    exit /b 1
)

if not exist "%ARCHIVE_DIR%" (
    echo Создание архива: %ARCHIVE_DIR%
    mkdir "%ARCHIVE_DIR%"
)

echo Удаление сессий старше %DAYS% дней (кроме important)...
echo.

powershell -NoProfile -Command ^
  "$threshold = (Get-Date).AddDays(-%DAYS%); ^
   $moved = 0; ^
   $skipped = 0; ^
   Get-ChildItem '%SESSIONS_DIR%\*.md' | Where-Object { ^
     $_.LastWriteTime -lt $threshold -and ^
     $_.Name -notlike '*important*' ^
   } | ForEach-Object { ^
     Move-Item $_.FullName -Destination '%ARCHIVE_DIR%\' -Force; ^
     Write-Host \"  [ARCHIVE] $_.Name\"; ^
     $moved++ ^
   }; ^
   Get-ChildItem '%SESSIONS_DIR%\*.md' | Where-Object { ^
     $_.LastWriteTime -lt $threshold -and ^
     $_.Name -like '*important*' ^
   } | ForEach-Object { ^
     Write-Host \"  [SKIP] $_.Name (important)\"; ^
     $skipped++ ^
   }; ^
   Write-Host \"\"; ^
   Write-Host \"Перемещено: $moved файлов\"; ^
   Write-Host \"Пропущено (important): $skipped файлов\""

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Очистка завершена.
    echo.
    echo Архив: %ARCHIVE_DIR%
) else (
    echo.
    echo ❌ Ошибка при очистке.
    exit /b 1
)
