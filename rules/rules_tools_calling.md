# Правила вызова инструментов (минимум)

## ПУТИ
### ЗАПЕЩЕНО
- любые системные пути Linux (`/usr/`, `/home/`, `/root/`,`/dev/` и так далее ) 
### Bash (`bash`)
- **Только** POSIX-пути с префиксом `/c/`: `ls -la /c/Project/Athenta/file.md`
- Диск C: → `/c/`, D: → `/d/`. Маленькая буква, без двоеточия.
- Обратный слеш `\` — **ЗАПРЕЩЁН**.

### Internal `read` (`read`)
- **Только** Windows-пути: `path="C:/Project/Athenta/file.md"`
- Прямой слеш `/`, диск с двоеточием `C:`.
- Никогда не используйте `/c/...` с инструментом `read`.

## ЧТЕНИЕ ФАЙЛОВ

| Ситуация | Инструмент | Команда |
|----------|-----------|---------|
| Простой файл, код, markdown | `bash` + `cat` | `cat /c/Project/Athenta/file.md` |
| Код с риском битого UTF-16 | `bash` + Python | `/c/Project/venv/Scripts/python.exe -c "import pathlib; print(pathlib.Path('/c/Project/Athenta/file.py').read_text(encoding='utf-8', errors='ignore'))"` |
| Поиск файлов по имени | `bash` + `find` | `find . -type d \( -name node_modules -o -name .git \) -prune -o -name "*.py" -print` |
| Поиск текста в файлах | `bash` + `grep`/`rg` | `grep -rn --binary-files=without-match --exclude-dir={node_modules,.git} "search_term" .` |
| Большой файл (>200 строк) | `bash` + `head`/`tail`/`sed` | `head -n 20 file && echo --- && tail -n 20 file` |

## ЗАПИСЬ ФАЙЛОВ

| Ситуация | Инструмент | Команда |
|----------|-----------|---------|
| Новый файл / полный перезапись | **Предпочтительно `write`** | — |
| Небольшой текст, шаблон | `bash` + Python | `/c/Project/venv/Scripts/python.exe -c "import pathlib; pathlib.Path('/c/Project/Athenta/file.md').write_text('content', encoding='utf-8')"` |
| Замена в существующем файле | `bash` + `sd` | `sd 'что_найти' 'чем_заменить' /c/Project/Athenta/file.py` (оба аргумента в одинарных кавычках) |
| Heredoc (если Python не подходит) | `bash` + `cat` | `cat << 'EOF' \| tr -d '\r' > /c/Project/Athenta/file.md` (закрытие EOF — на отдельной строке, без пробелов) |

## ЗАПУСК PYTHON
- **Всегда** полный путь: `/c/Project/venv/Scripts/python.exe`
- Не `python`, не `C:\...`, не `/c/Project/venv/Scripts/python` (без `.exe`)
- Внутри двойных кавычек `-c "..."` — пути в одинарных `'...'`

## АЛГОРИТМ ЛЮБОЙ КОМАНДЫ
1. `ls -la /путь/к/файлу` → убедиться что файл существует
2. Написать команду с правильными путями и кавычками
3. Выполнить через `bash`
4. При ошибке — исправить, выполнить снова

## МАРКЕРЫ КОНЦА ФАЙЛОВ (обязательно)
- `.md` → в конец: `[EOF_TODO_SUCCESS]`
- `.py` → в конец: `# [EOF_CODE_SUCCESS]`
