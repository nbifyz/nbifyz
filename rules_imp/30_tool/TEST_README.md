# V3 System Testing Guide
## Руководство по тестированию АГЕНТ-V3

**Версия:** 1.0
**Дата:** 2026-03-30
**Файл тестов:** `test_v3_system.py`

---

## Быстрый старт

```bash
# Тестировать всю систему
python test_v3_system.py

# Подробный вывод
python test_v3_system.py --verbose

# Тестировать конкретный компонент
python test_v3_system.py --component gatekeeper
python test_v3_system.py --component pre_run
python test_v3_system.py --component session
python test_v3_system.py --component file_guard
python test_v3_system.py --component auto_lesson
```

---

## Структура тестов

### 1. Gatekeeper Tests
- **PoS-1**: Блокировка утверждений без Proof of Search
- **PoS-2**: Разрешение утверждений с PoS маркерами
- **Honest-1**: Блокировка расплывчатых статусов ("выполнено")
- **Honest-2**: Разрешение X/Y формата ("выполнено: 5 из 10")
- **Code-1**: Обнаружение синтаксических ошибок Python
- **Code-2**: Разрешение валидного кода Python
- **Path-1**: Обнаружение обратных слешей в bash
- **Path-2**: Обнаружение `@` в именах файлов

### 2. Pre-run Validator Tests
- **Bash-1**: Блокировка команд с `\` в пути
- **Bash-2**: Блокировка команд с `@` в имени файла
- **JSON-1**: Проверка формата путей для JSON (`\\`)
- **Auto-correct**: Автоисправление путей ( `\` → `/` )

### 3. Session Gate Tests
- **Session-1**: Разрешение сессии с валидным lesson
- **Lesson-1**: Получение текущего lesson
- **Metadata-1**: Валидация JSON метаданных в lesson

### 4. File Access Guard Tests
- **Write-1**: Проверка записи в существующий файл
- **EPERM-1**: Диагностика ошибок доступа
- **Missing**: Обработка несуществующих файлов

### 5. Auto Lesson Creator Tests
- **Error-1**: Создание lesson из ошибки
- **Reflection-1**: Создание lesson из инсайта
- **Knowledge-1**: Создание lesson из знания
- **Metadata-2**: Проверка JSON метаданных в созданном lesson

---

## Ручное тестирование

### Gatekeeper CLI
```bash
python gatekeeper.py --check pos --value "Функция X в файле Y"
python gatekeeper.py --check honest --value "Выполнено"
python gatekeeper.py --check path --value "C:\\path\\file"
python gatekeeper.py --check session
```

### Pre-run Validator CLI
```bash
python pre_run_validator.py 'cat C:\\path\\file.txt' --check bash
python pre_run_validator.py 'C:/path/file' --check json
python pre_run_validator.py 'cat C:\\path\\file.txt' --auto-correct
```

### Session Gate CLI
```bash
python session_gate.py --check
python session_gate.py --get-lesson
```

### File Access Guard CLI
```bash
python file_access_guard.py C:/test.txt --before-write
python file_access_guard.py C:/test.txt --diagnose
python file_access_guard.py --remove-readonly-dir
```

### Auto Lesson Creator CLI
```bash
python auto_lesson_creator.py --type error --topic "TEST" --content "Test" --priority HIGH
python auto_lesson_creator.py --type reflection --topic "Insight" --content "Knowledge" --priority MEDIUM
```

---

## Интерпретация результатов

### Вывод тестов
```
✓ Test Name          # Тест пройден
✗ Test Name          # Тест не пройден
⚠ Test Name          # Предупреждение (не критично)
```

### Коды возврата
- **0** — Все тесты пройдены
- **1** — Есть ошибки

---

## Тестовые данные

### Lesson файл для тестирования
Создан автоматически: `C:/CLI/Pi/lessons/lesson_2026-03-30_TEST_V3_System.md`

Содержит валидные JSON метаданные для проверки Session Gate.

---

## Интеграционное тестирование

### Полный сценарий работы

```python
# 1. Проверка сессии
from session_gate import check_session
allowed, msg, lesson = check_session()
assert allowed, "Session should be allowed with test lesson"

# 2. Проверка команды перед bash
from pre_run_validator import before_bash
allowed, msg, corrected = before_bash('cat C:\\path\\file.txt')
assert not allowed, "Should block backslash"

# 3. Проверка утверждения
from gatekeeper import require_proof_of_search
allowed, msg = require_proof_of_search("Функция X в файле Y")
assert not allowed, "Should require PoS"

# 4. Проверка файла перед записью
from file_access_guard import before_write
allowed, msg = before_write("C:/test.txt")
assert allowed, "Should allow writing"

# 5. Создание lesson (безусловно)
from auto_lesson_creator import lesson_from_reflection
success, path, msg = lesson_from_reflection("Test", "Insight")
assert success, "Should create lesson"
```

---

## Отладка

### Проверка логов
```bash
# Violations
Get-Content C:/CLI/Pi/sessions/gatekeeper_violations.log -Tail 10
Get-Content C:/CLI/Pi/sessions/prerun_violations.log -Tail 10
Get-Content C:/CLI/Pi/sessions/session_blocks.log -Tail 10

# Approvals
Get-Content C:/CLI/Pi/sessions/gatekeeper_approvals.log -Tail 10
Get-Content C:/CLI/Pi/sessions/session_approvals.log -Tail 10

# Lesson creation
Get-Content C:/CLI/Pi/sessions/auto_lesson_creator.log -Tail 10
```

---

## Чек-лист приемки

- [ ] Gatekeeper блокирует утверждения без PoS
- [ ] Gatekeeper блокирует "выполнено" без X/Y
- [ ] Gatekeeper проверяет синтаксис Python
- [ ] Pre-run Validator блокирует `\` в bash
- [ ] Pre-run Validator блокирует `@` в именах
- [ ] Session Gate разрешает сессию с lesson
- [ ] Session Gate наход lesson с JSON метаданными
- [ ] File Access Guard снимает Read-Only
- [ ] File Access Guard диагностирует EPERM
- [ ] Auto Lesson создает файлы без вопросов
- [ ] Все инструменты имеют CLI
- [ ] Тесты проходят (`python test_v3_system.py`)

---

**Статус:** Готово к тестированию
