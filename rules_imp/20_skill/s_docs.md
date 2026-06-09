# 📝 Скилл 5: Документирование кода

## Правило

**ВСЕГДА** документировать функции, классы и модули.

## Docstring шаблон

```python
def process_file(path: str, encoding: str = 'utf-8') -> str | None:
    """
    Обрабатывает файл и возвращает его содержимое.

    Args:
        path: Путь к файлу
        encoding: Кодировка файла (по умолчанию: utf-8)

    Returns:
        Содержимое файла или None при ошибке

    Raises:
        FileNotFoundError: Если файл не существует
        PermissionError: Нет доступа к файлу
    """
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        return None
    # ... rest of code
```

## Что документировать

- ✅ Функции и их параметры
- ✅ Возвращаемые значения
- ✅ Возможные исключения
- ✅ Примеры использования

---

**Дата создания:** 2026-02-11
