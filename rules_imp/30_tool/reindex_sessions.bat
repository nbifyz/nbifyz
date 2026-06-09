@echo off
chcp 65001 > nul
echo ============================================
echo Перестроение индекса сессий
echo ============================================
echo.

set "SESSIONS_DIR=sessions"
set "INDEX_FILE=%SESSIONS_DIR%\index.json"

if not exist "%SESSIONS_DIR%" (
    echo Каталог сессий не найден: %SESSIONS_DIR%
    exit /b 1
)

echo Сканирование сессий...
powershell -NoProfile -Command ^
  "$sessions = Get-ChildItem '%SESSIONS_DIR%\*.md' | ForEach-Object { ^
    $name = $_.Name; ^
    $tags = @(); ^
    $important = $false; ^
    $summary = ''; ^
    if ($name -match '_([^_]+)\.md$') { ^
      $match = $matches[1]; ^
      if ($match -ne 'important') { $tags = $match -split ',' } ^
    }; ^
    if ($name -match 'important') { $important = $true }; ^
    [PSCustomObject]@{ ^
      file = $name; ^
      created = $_.LastWriteTime.ToString('o'); ^
      tags = $tags; ^
      summary = $summary; ^
      important = $important ^
    } ^
  }; ^
  $json = @{ ^
    sessions = $sessions; ^
    last_updated = (Get-Date).ToString('o'); ^
    total_sessions = $sessions.Count ^
  }; ^
  $json | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 '%INDEX_FILE%'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Индекс сессий перестроен.
    echo.
    echo Файл: %INDEX_FILE%
) else (
    echo.
    echo ❌ Ошибка при перестроении индекса.
    exit /b 1
)
