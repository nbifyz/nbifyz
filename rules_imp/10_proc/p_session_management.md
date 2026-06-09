# Протокол Управления Сессиями (p_session_management.md)

**Принцип:** V. Session Management & Continuity (Non-Negotiable)  
**Версия:** 1.0.0  
**Создан:** 2026-03-29

---

## Назначение

Этот протокол обеспечивает **полное управление сессиями**: сохранение, загрузка, изучение, архивирование.

---

## Структура Хранения

```
sessions/
├── index.json                    # Индекс всех сессий
├── YYYY-MM-DD_HH-MM-SS_[теги].md # Файлы сессий
├── archive/                      # Архив (>30 дней)
└── templates/                    # Шаблоны (опционально)
```

### Формат Имени Файла

```
YYYY-MM-DD_HH-MM-SS_[теги].md
```

**Примеры:**
- `2026-03-29_14-30-00.md` — базовый формат
- `2026-03-29_14-30-00_bugfix.md` — с тегами
- `2026-03-29_14-30-00_important.md` — важная сессия

---

## Индекс Сессий (`sessions/index.json`)

### Формат

```json
{
  "sessions": [
    {
      "file": "2026-03-29_14-30-00.md",
      "created": "2026-03-29T14:30:00",
      "tags": ["bugfix", "rules"],
      "summary": "Исправление ошибки EPERM",
      "important": false,
      "lessons_created": ["Диагностика_ошибок_доступа_к_файлам.md"]
    }
  ],
  "last_updated": "2026-03-29T16:45:00"
}
```

---

## Команды Управления Сессиями

| Команда | Описание |
|---------|----------|
| `/sessions list` | Список сессий |
| `/sessions load <имя>` | Загрузить сессию |
| `/sessions tag <имя> <теги>` | Добавить теги |
| `/sessions summary <имя> [текст]` | Установить summary |
| `/sessions important <имя>` | Пометить важной |
| `/sessions search <запрос>` | Поиск по сессиям |
| `/sessions archive <имя>` | Архивировать |
| `/sessions restore <имя>` | Восстановить из архива |
| `/sessions clean` | Очистка (>30 дней) |
| `/sessions reindex` | Перестроить индекс |
| `/save [теги]` | Сохранить текущую |
| `/load <имя>` | Загрузить сессию |

---

## Процедура "Консервации" (при 120K контекста)

**Шаги:**

1. **Суммировать [HISTORY]** в 5-7 тезисов
2. **Сохранить "сало" на диск:**
   ```
   sessions/id_session_dd-mm-yyyy_hh-mm.md
   ```
3. **Удалить из RAM:**
   - code_listings (есть в файлах проекта)
   - detailed_descriptions (суммировать)
   - plot_developments (ключевые события → в лог)

---

## Скрипты

### reindex_sessions.bat

```batch
@echo off
chcp 65001 > nul
powershell -NoProfile -Command ^
  "$sessions = Get-ChildItem 'sessions\*.md' | ForEach-Object { ^
    [PSCustomObject]@{ ^
      file = $_.Name; ^
      created = $_.LastWriteTime.ToString('o'); ^
      tags = @(); ^
      summary = ''; ^
      important = $false ^
    } ^
  }; ^
  $sessions | ConvertTo-Json | Set-Content -Encoding UTF8 'sessions\index.json'"
echo Индекс сессий обновлён.
```

### clean_sessions.bat

```batch
@echo off
chcp 65001 > nul
set "ARCHIVE_DIR=sessions\archive"
if not exist "%ARCHIVE_DIR%" mkdir "%ARCHIVE_DIR%"
powershell -NoProfile -Command ^
  "$threshold = (Get-Date).AddDays(-30); ^
   Get-ChildItem 'sessions\*.md' | Where-Object { ^
     $_.LastWriteTime -lt $threshold -and ^
     $_.Name -notlike '*important*' ^
   } | ForEach-Object { ^
     Move-Item $_.FullName -Destination '%ARCHIVE_DIR%\' -Force ^
   }"
echo Очистка завершена.
```

---

## Чек-лист Валидации

- [ ] Сессия сохранена в sessions/YYYY-MM-DD_HH-MM-SS_[теги].md?
- [ ] sessions/index.json обновлён?
- [ ] Теги и summary добавлены?
- [ ] 12 команд работают?
- [ ] Авто-перестроение index.json при повреждении?
- [ ] Очистка >30 дней работает (кроме important)?

---

**Статус:** ✅ ACTIVE  
**Интегрировано в:** constitution.md (Принцип V), spec.md (FR-010 — FR-014, FR-017)
