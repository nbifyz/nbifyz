# ПРАВИЛО ПУТЕЙ ДЛЯ Pi (Windows)

**Версия:** 1.1.0  
**Принцип:** I. Truthfulness — точность в путях

---

## 📋 КРАТКОЕ ПРАВИЛО

| Контекст | Формат | Пример |
|----------|--------|--------|
| **Терминал (bash/powershell)** | Прямые слеши `/` + кавычки | `"C:/CLI/Pi/rules_imp"` |
| **JSON-конфиг** | Двойные слеши `\\` | `"path": "C:\\CLI\\Pi\\rules_imp"` |
| **Текст (Markdown)** | Одинарные слеши `\` | `%RULES%\00_core\id.md` |
| **BAT-файлы** | Одинарные слеши `\` | `set "RULES=C:\CLI\Pi\rules_imp"` |
| **.env файл** | Одинарные слеши `\` | `RULES=C:\CLI\Pi\rules_imp` |

---

## 📝 ДЕТАЛЬНЫЕ ПРИМЕРЫ

### 1. Терминал (bash / PowerShell)

**Правильно:**
```bash
pi --rules "C:/CLI/Pi/rules_imp"
rg "термин" "C:/CLI/Pi/rules_imp/00_core/"
```

**Неправильно:**
```bash
pi --rules C:\CLI\Pi\rules_imp  # ❌ обратные слеши без кавычек
```

---

### 2. JSON-конфиг / Tool Call

**Правильно:**
```json
{
  "action": "read_file",
  "args": {
    "path": "C:\\CLI\\Pi\\rules_imp\\00_core\\id.md"
  }
}
```

**Неправильно:**
```json
{
  "action": "read_file",
  "args": {
    "path": "C:/CLI/Pi/rules_imp/00_core/id.md"  # ❌ прямые слеши в JSON
  }
}
```

---

### 3. Текст в Markdown (AGENTS.md, QWEN.md)

**Правильно:**
```markdown
Путь к файлу: `%RULES%\00_core\id.md`
Протокол: `rules_imp/10_proc/p_safe_edit.md`
```

**Неправильно:**
```markdown
Путь к файлу: `C:\\CLI\\Pi\\rules_imp`  # ❌ двойные слеши в тексте
```

---

### 4. BAT-файлы

**Правильно:**
```batch
set "RULES=C:\CLI\Pi\rules_imp"
call "%RULES%\30_tool\check-dependencies.bat"
```

**Неправильно:**
```batch
set "RULES=C:/CLI/Pi/rules_imp"  # ❌ прямые слеши в BAT
```

---

### 5. .env файл

**Правильно:**
```env
PB=C:\CLI\Pi
RULES=C:\CLI\Pi\rules_imp
PS=C:\CLI\Pi\sessions
```

**Неправильно:**
```env
RULES=C:/CLI/Pi/rules_imp  # ❌ прямые слеши в .env
```

---

## 🎯 ЗАПОМНИТЬ

> **В терминале — `/` (прямые), в JSON — `\\` (двойные обратные), в тексте/BAT/.env — `\` (одинарные).**

**Остальное — ошибка.**

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ

- `AGENTS.md` — раздел "Tool Call Format (STRICT)"
- `.env` — переменные окружения
- `load_env.bat` — загрузка переменных
