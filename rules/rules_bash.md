# Файл `ruses_bash.md`
# ПАМЯТКА ПО BASH-КОМАНДАМ В WINDOWS (GIT BASH)
При конфликте с AGENTS.md — следовать AGENTS.md
## 1. ЗОЛОТОЕ ПРАВИЛО
**Никогда не используй обратный слеш `\`.**  
Всегда **только прямой слеш `/`**.  
Windows-диск C: → `/c/`, диск D: → `/d/`.

## 2. ПУТИ (САМАЯ ЧАСТАЯ ОШИБКА)
| Что хочешь | Неправильно | Правильно |
|------------|-------------|-----------|
| Файл на диске C | `C:\Project\file.txt` | `/c/Project/file.txt` |
| Файл на диске D | `D:\data\file.txt` | `/d/data/file.txt` |
| Текущая папка | `.\script.py` | `./script.py` |
| Родительская папка | `..\folder` | `../folder` |

**Важно:** в Git Bash буква диска **маленькая**, без двоеточия.

## 3. ПРОВЕРКА ПЕРЕД ЛЮБОЙ КОМАНДОЙ
**Сначала всегда проверяй, существует ли путь:**
```bash
ls -la /c/Project/Athenta/Media2Opus/.specify/
```
Если `ls` показывает `No such file or directory` — **не запускай Python**, ищи ошибку в пути.

## 4. ПРАВИЛЬНЫЙ ЗАПУСК PYTHON-СКРИПТОВ
Виртуальное окружение: `/c/Project/venv/Scripts/python.exe`

**Неправильно:**
```bash
python script.py
C:\Project\venv\Scripts\python.exe
/c/Project/venv/Scripts/python
```

**Правильно:**
```bash
/c/Project/venv/Scripts/python.exe /c/Project/script.py
```

## 5. КАВЫЧКИ И ПРОБЕЛЫ
- Если в пути есть пробелы — бери весь путь в **двойные кавычки** `"..."`.
- Внутри `python -c "..."` используй **одинарные кавычки** для вложенных путей.

**Пример с пробелом:**
```bash
cat "/c/Program Files/some file.txt"
```

**Пример с python -c:**
```bash
/c/Project/venv/Scripts/python.exe -c "import yaml; print(yaml.safe_load(open('/c/Project/file.yml')))"
```
(внутри двойных кавычек — одинарные)

## 6. ЧАСТЫЕ ОШИБКИ АГЕНТА И ИХ РЕШЕНИЕ

| Ошибка агента | Почему | Как правильно |
|---------------|--------|----------------|
| `cat C:\Project\file.txt` | Использует обратный слеш | `cat /c/Project/file.txt` |
| `python script.py` | Не указан полный путь к python.exe | `/c/Project/venv/Scripts/python.exe script.py` |
| `/c/Project/venv/Scripts/python` | Забыл `.exe` | `/c/Project/venv/Scripts/python.exe` |
| `cd \Project` | Начинает с обратного слеша | `cd /c/Project` |
| Забывает проверить существование файла | Не вызывает `ls` перед основной командой | Сначала `ls -la /путь/к/файлу` |

## 7. АЛГОРИТМ ВЫПОЛНЕНИЯ ЛЮБОЙ BASH-КОМАНДЫ
1. **Проверить путь через `ls -la`** — если нет файла, остановиться.
2. **Написать команду** с правильными `/c/`, `.exe`, кавычками.
3. **Выполнить**.
4. **Если ошибка** — прочитать вывод, исправить путь или синтаксис, выполнить снова.

## 8. БЫСТРЫЙ ТЕСТ — ЭТА КОМАНДА ДОЛЖНА РАБОТАТЬ
```bash
/c/Project/venv/Scripts/python.exe --version
```
Должно вывести версию Python. Если не работает — значит, неправильный путь к venv.

[EOF_TODO_SUCCESS]

