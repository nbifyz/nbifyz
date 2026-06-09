# V3 QUICK START
## Быстрый старт с АГЕНТ-V3

**Версия:** 3.0
**Дата:** 2026-03-30
**Время чтения:** 10 минут
**Статус:** ✅ Готово к использованию

---

## ЧТО ТАКОЕ V3

V3 — это система жестких блокировок, которая технически предотвращает нарушение правил:
- **Не просит** — блокирует автоматически
- **Не предупреждает** — физически останавливает
- **Не «рекомендует»** — требует исправления

---

## 5 МИНУТ ДО РАБОТЫ

### Шаг 1: Проверка окружения

Открой PowerShell в директории `C:/CLI/Pi`:

```powershell
# Проверить Python
python --version  # Должно быть 3.8+

# Проверить структуру
ls rules_imp/30_tool/*.py
ls lessons/templates/
```

**Ожидаемый результат:**
```
gatekeeper.py
pre_run_validator.py
session_gate.py
file_access_guard.py
auto_lesson_creator.py
test_v3_system.py
lesson_template.md
```

### Шаг 2: Запуск тестов

```powershell
cd C:/CLI/Pi/rules_imp/30_tool
python test_v3_system.py
```

**Успех:** `[OK] ВСЕ ТЕСТЫ ПРОЙДЕНЫ`

**Провал:** Смотри раздел «Решение проблем»

### Шаг 3: Проверка lesson

```powershell
python session_gate.py --check
```

**Успех:** `Session Allowed: True` + путь к lesson

**Провал:** Создай lesson (см. раздел «Создание lesson»)

### Шаг 4: Первый тест блокировки

```powershell
python gatekeeper.py --check pos --value "Функция X в файле Y"
```

**Ожидаемо:** `Allowed: False` + сообщение о требовании PoS

**Если True:** Проверь версию gatekeeper.py

---

## КАЖДОДНЕВНАЯ РАБОТА

### Утро: Открытие сессии

```python
# В начале Python-скрипта
import sys
sys.path.insert(0, "C:/CLI/Pi/rules_imp/30_tool")

from session_gate import check_session

# ЭТА СТРОКА ОБЯЗАТЕЛЬНА
allowed, msg, lesson = check_session()
if not allowed:
    print(f"[BLOCKED] {msg}")
    sys.exit(1)

print(f"Сессия открыта с lesson: {lesson}")
```

### Перед любым bash

```python
from pre_run_validator import before_bash

command = 'cat C:/some/path/file.txt'
allowed, msg, corrected = before_bash(command)

if not allowed:
    print(f"[BLOCKED] {msg}")
    if corrected:
        print(f"Используй: {corrected}")
    # КОМАНДА НЕ УЙДЕТ В BASH
```

### Перед утверждением о коде

```python
from gatekeeper import require_proof_of_search

claim = "Функция process находится в utils.py"
allowed, msg = require_proof_of_search(claim)

if not allowed:
    print(f"[BLOCKED] {msg}")
    # Добавь:
    # rg -nH 'def process' C:/project
    # Файл: utils.py:42
    # Код: def process(data):
    # PoS: Данные взяты из исходника
```

### После ошибки (авто)

```python
from auto_lesson_creator import lesson_from_error

# НЕ СПРАШИВАЕТ, НЕ ЖДЕТ ПОДТВЕРЖДЕНИЯ
# Создается БЕЗУСЛОВНО

try:
    risky_operation()
except Exception as e:
    lesson_from_error(
        error_type="RuntimeError",
        error_message=str(e),
        context="Во время обработки файла X",
        priority="HIGH"
    )
    # lesson_2026-03-30_ERROR_RuntimeError_123456.md создан
    raise
```

---

## СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ

### Сценарий 1: Запретить «выполнено» без X/Y

**Проблема:** Агент говорит «готово», но задачи частично выполнены

**Решение:**
```python
from gatekeeper import require_honest_reporting

status = "Выполнено: 7 из 10 задач (70%)"
allowed, msg = require_honest_reporting(
    status,
    total=10,
    completed=7
)

if not allowed:
    # БЛОКИРОВКА — должно быть "7 из 10"
    pass
```

### Сценарий 2: Поймать неверный путь

**Проблема:** Команда с `C:\path\file` вместо `C:/path/file`

**Решение:**
```python
from pre_run_validator import before_bash, auto_correct_path

command = 'cat C:\\path\\to\\file.txt'
allowed, msg, corrected = before_bash(command)

if not allowed:
    # Исправленная версия
    fixed = auto_correct_path(command)
    # 'cat "C:/path/to/file.txt"'
```

### Сценарий 3: Авто-исправление Read-Only

**Проблема:** Файл внезапно стал Read-Only

**Решение:**
```python
from file_access_guard import before_write

can_write, msg = before_write("C:/CLI/Pi/rules_imp/file.md")
if can_write:
    # Если был Read-Only — уже снят автоматически
    write_file()
```

### Сценарий 4: Блокировка без lesson

**Проблема:** Начинаешь работу, но забыл создать lesson

**Решение:**
```python
from session_gate import check_session

allowed, msg, lesson = check_session()
if not allowed:
    # БЛОКИРОВКА — создай lesson first
    print(msg)
    # Инструкция как создать lesson...
```

---

## СОЗДАНИЕ LESSON

### Быстрый способ

```python
from auto_lesson_creator import lesson_from_reflection

lesson_from_reflection(
    topic="Работа над Task #123",
    insight="Обнаружил, что X работает через Y",
    application="В следующий раз проверять Y первым",
    priority="MEDIUM"
)
```

**Результат:**
- Файл: `lesson_2026-03-30_REFL_Работа_над_Task_123_HHMMSS.md`
- С JSON метаданными
- Сессия сразу откроется

### Ручной способ

1. Скопируй `lesson_template.md`
2. Заполни JSON в начале:
```json
---
{
  "date": "2026-03-30",
  "topic": "Название",
  "priority": "HIGH",
  "type": "reflection",
  "tags": ["work", "v3"]
}
---
```
3. Сохрани как `lesson_2026-03-30_[тема].md`
4. Готово — сессия откроется

---

## КЛЮЧЕВЫЕ КОМАНДЫ CLI

```bash
# Gatekeeper
python gatekeeper.py --check pos --value "текст"
python gatekeeper.py --check honest --value "Выполнено"
python gatekeeper.py --check path --value "C:\\path"
python gatekeeper.py --check session

# Pre-run Validator
python pre_run_validator.py 'команда' --check bash
python pre_run_validator.py 'C:/path' --check json

# Session Gate
python session_gate.py --check
python session_gate.py --get-lesson

# File Access Guard
python file_access_guard.py C:/file.txt --before-write
python file_access_guard.py C:/file.txt --diagnose

# Auto Lesson Creator
python auto_lesson_creator.py --type error --topic "NAME" --content "TEXT" --priority HIGH
python auto_lesson_creator.py --type reflection --topic "NAME" --content "INSIGHT" --priority MEDIUM

# Тестирование
python test_v3_system.py
python test_v3_system.py --verbose
python test_v3_system.py --component gatekeeper
```

---

## ИНТЕГРАЦИЯ В РАБОЧИЙ ПРОЦЕСС

### Шаблон начала скрипта

```python
#!/usr/bin/env python3
"""
Название задачи
"""

import sys
sys.path.insert(0, "C:/CLI/Pi/rules_imp/30_tool")

# === V3 MANDATORY CHECKS ===
from session_gate import check_session
from gatekeeper import require_proof_of_search
from pre_run_validator import before_bash
from file_access_guard import before_write

# 1. Session check
allowed, msg, lesson = check_session()
if not allowed:
    print(f"[V3 BLOCKED] {msg}")
    sys.exit(1)

print(f"[V3] Session opened with {lesson.name}")

# === ВАШ КОД ЗДЕСЬ ===
```

### Шаблон перед bash

```python
from pre_run_validator import before_bash

def safe_bash(command):
    """Обёртка с V3 проверкой"""
    allowed, msg, corrected = before_bash(command)
    if not allowed:
        print(f"[V3 BLOCKED] {msg}")
        if corrected:
            print(f"[V3 SUGGESTION] {corrected}")
        return False
    # Только теперь выполнять
    return True

# Использование
if safe_bash('cat C:/path/file.txt'):
    # Выполнить команду
    pass
```

### Шаблон проверки кода

```python
from gatekeeper import require_code_accuracy

def safe_python_write(filepath, code):
    """Запись Python с проверкой синтаксиса"""
    if filepath.endswith('.py'):
        allowed, msg = require_code_accuracy(code, 'python')
        if not allowed:
            print(f"[V3 BLOCKED] {msg}")
            return False
    # Записать файл
    return True
```

---

## РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Session Gate отказывает

**Причина:** Нет lesson за сегодня

**Решение:**
```powershell
python auto_lesson_creator.py --type reflection --topic "Daily" --content "Work session" --priority MEDIUM
```

### Проблема: Тесты не проходят

**Проверь:**
1. Python 3.8+: `python --version`
2. Путь к инструментам: `ls C:/CLI/Pi/rules_imp/30_tool/`
3. Кодировка UTF-8: `chcp 65001`

### Проблема: ImportError

**Решение:**
```python
import sys
sys.path.insert(0, "C:/CLI/Pi/rules_imp/30_tool")
```

### Проблема: Файлы Read-Only

**Быстрое решение:**
```powershell
python file_access_guard.py --remove-readonly-dir C:/CLI/Pi/rules_imp
```

---

## БЫСТРЫЕ ССЫЛКИ

### Документы
- `C:/CLI/Pi/rules_imp/00_core/constitution.md` — 5 принципов
- `C:/CLI/Pi/rules_imp/00_core/hierarchy.md` — приоритеты правил
- `C:/CLI/Pi/rules_imp/00_core/EPERM_REFERENCE.md` — ошибки доступа
- `C:/CLI/Pi/rules_imp/30_tool/TEST_README.md` — тестирование

### Логи
```powershell
Get-Content C:/CLI/Pi/sessions/gatekeeper_violations.log -Tail 5
Get-Content C:/CLI/Pi/sessions/session_blocks.log -Tail 5
Get-Content C:/CLI/Pi/sessions/auto_lesson_creator.log -Tail 5
```

### Обновление
```powershell
cd C:/CLI/Pi/rules_imp/30_tool
python test_v3_system.py
```

---

## ЧЕК-ЛИСТ КАЖДОГО ДНЯ

- [ ] Запустить `python test_v3_system.py` — все ОК?
- [ ] Проверить `python session_gate.py --check` — session allowed?
- [ ] Убедиться, что lesson создан за сегодня
- [ ] Готово к работе!

---

## 3 ВЕЩИ, КОТОРЫЕ НЕЛЬЗЯ ЗАБЫВАТЬ

1. **Session Gate** — всегда проверяй перед началом
2. **Pre-run** — всегда валидируй bash команды
3. **Auto Lesson** — при любой ошибке создавай lesson БЕЗУСЛОВНО

---

## ПОМОЩЬ

Если что-то не работает:

1. Проверь тесты: `python test_v3_system.py`
2. Проверь логи: `Get-Content sessions/*.log -Tail 10`
3. Проверь lesson: `python session_gate.py --check`
4. Перечитай этот файл

---

**Вы готовы работать с V3!**

Запусти: `python test_v3_system.py` и начинай.
