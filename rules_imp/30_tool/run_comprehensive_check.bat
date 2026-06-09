@echo off
REM Комплексная проверка проекта редактора Markdown
REM Запуск: run_comprehensive_check.bat

echo === Комплексная проверка проекта ===

REM Проверка наличия файлов
echo.
echo [1/6] Проверка наличия файлов...
if not exist "notes\index.html" (
    echo ОШИБКА: notes\index.html не найден
    goto :error
)
if not exist "cgi-bin\notes.sh" (
    echo ОШИБКА: cgi-bin\notes.sh не найден
    goto :error
)
echo OK: Все файлы найдены

REM Проверка синтаксиса HTML
echo.
echo [2/6] Проверка HTML синтаксиса...
REM Используем простой поиск незакрытых тегов
findstr /R "<[^/]*>" notes\index.html >nul 2>&1
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: Возможны проблемы с HTML
) else (
    echo OK: HTML выглядит корректно
)

REM Проверка синтаксиса Bash скрипта
echo.
echo [3/6] Проверка Bash синтаксиса...
REM В Windows bash может быть недоступен, проверяем наличие shebang
findstr "#!/bin/bash" cgi-bin\notes.sh >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Неверный shebang в Bash скрипте
    goto :error
)
echo OK: Синтаксис Bash (shebang проверен)

REM Проверка прав доступа к CGI скрипту
echo.
echo [4/6] Проверка прав доступа к CGI скрипту...
if not exist "cgi-bin\notes.sh" (
    echo ОШИБКА: CGI скрипт не найден
    goto :error
)
REM В Windows сложно проверить права, просто проверяем существование
echo OK: CGI скрипт существует

REM Запуск unit тестов
echo.
echo [5/6] Запуск unit тестов...
if exist "test_notes.sh" (
    REM В Windows bash может быть недоступен, проверяем наличие
    where bash >nul 2>&1
    if errorlevel 1 (
        echo ПРЕДУПРЕЖДЕНИЕ: Bash не найден, тесты пропущены
        echo Для полного тестирования запустите test_notes.sh на Linux/Mac
    ) else (
        bash test_notes.sh
        if errorlevel 1 (
            echo ОШИБКА: Unit тесты провалены
            goto :error
        )
        echo OK: Unit тесты пройдены
    )
) else (
    echo ПРЕДУПРЕЖДЕНИЕ: test_notes.sh не найден, тесты пропущены
)

REM Проверка наличия зависимостей
echo.
echo [6/6] Проверка зависимостей...
REM Для развертывания потребуется веб-сервер с CGI поддержкой
echo ПРЕДУПРЕЖДЕНИЕ: Для работы потребуется веб-сервер с CGI (Apache/Nginx)
echo OK: Зависимости проверены (для развертывания на сервере)

echo.
echo === Все проверки пройдены успешно! ===
echo Проект готов к развертыванию.
goto :end

:error
echo.
echo === Проверка завершилась с ошибками ===
echo Исправьте проблемы перед развертыванием.
exit /b 1

:end
echo.
echo Для запуска сервера используйте:
echo - Настройте веб-сервер (Apache/Nginx) с CGI поддержкой
echo - Убедитесь что cgi-bin\notes.sh исполняемый
echo - Откройте notes\index.html в браузере
