# ✅ Скилл 6: Валидация данных

## Правило

**ВСЕГДА** проверять входные данные перед обработкой.

## Шаблон

```python
def process_user_input(text: str, max_length: int = 1000) -> str:
    """
    Валидирует и обрабатывает ввод пользователя.

    Args:
        text: Введенный текст
        max_length: Максимальная длина

    Returns:
        Очищенный текст

    Raises:
        ValueError: При некорректных данных
    """
    # Проверка типа
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")

    # Проверка пустоты
    if not text.strip():
        raise ValueError("Empty input")

    # Проверка длины
    if len(text) > max_length:
        raise ValueError(f"Input too long: {len(text)} > {max_length}")

    # Очистка
    cleaned = text.strip()

    return cleaned
```

## Что валидировать

- ✅ Типы данных
- ✅ Диапазоны значений
- ✅ Форматы (email, url, пути)
- ✅ Наличие обязательных полей

---

**Дата создания:** 2026-02-11
