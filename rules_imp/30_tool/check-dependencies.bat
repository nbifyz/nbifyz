@echo off
chcp 65001 > nul
echo ============================================
echo Проверка зависимостей (rg, sd)
echo ============================================
echo.

set RG_FOUND=0
set SD_FOUND=0

:: Проверка rg (ripgrep)
echo [1/2] Проверка ripgrep (rg)...
where rg >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    - rg найдена
    set RG_FOUND=1
) else (
    echo    - rg НЕ найдена
    echo.
    echo   Установка через winget:
    echo     winget install ripgrep
    echo.
    echo   Установка через choco:
    echo     choco install ripgrep
)
echo.

:: Проверка sd (search & displace)
echo [2/2] Проверка search & displace (sd)...
where sd >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    - sd найдена
    set SD_FOUND=1
) else (
    echo    - sd НЕ найдена
    echo.
    echo   Установка через choco:
    echo     choco install sd
)
echo.

:: Итоговый отчёт
echo ============================================
echo ИТОГОВЫЙ ОТЧЁТ
echo ============================================
echo.

if %RG_FOUND% EQU 1 (
    echo   ripgrep ^(rg^):        [OK] Установлен
) else (
    echo   ripgrep ^(rg^):        [FAIL] НЕ установлен
)

if %SD_FOUND% EQU 1 (
    echo   search ^& displace ^(sd^):  [OK] Установлен
) else (
    echo   search ^& displace ^(sd^):  [FAIL] НЕ установлен
)

echo.

:: Вычисление процента
set /a INSTALLED=%RG_FOUND%+%SD_FOUND%
set /a PERCENT=(%INSTALLED%*100)/2

echo ============================================
echo Честный отчёт о частичном выполнении
echo ============================================
echo.
echo Найдено: %INSTALLED% из 2 (%PERCENT%%)
echo.

if %INSTALLED% EQU 2 (
    echo Все зависимости установлены.
    echo.
    exit /b 0
) else (
    echo.
    echo Список ненайденных утилит:
    if %RG_FOUND% EQU 0 echo   - ripgrep (rg)
    if %SD_FOUND% EQU 0 echo   - search & displace (sd)
    echo.
    echo Предложение:
    echo   Повторить проверку через 10 минут после установки
    echo   отсутствующих утилит.
    echo.
    exit /b 1
)
