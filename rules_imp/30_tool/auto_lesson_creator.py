#!/usr/bin/env python3
"""
AUTO LESSON CREATOR V3 — Безусловная Запись Уроков
Создает lesson файлы автоматически, без вопросов и подтверждений

Версия: 3.0
Дата: 2026-03-30
Приоритет: КРИТИЧЕСКИЙ
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any


class AutoLessonCreatorError(Exception):
    """Исключение при ошибке создания урока"""
    pass


class AutoLessonCreator:
    """
    Создатель уроков V3.
    БЕЗУСЛОВНО создает lesson при:
    - Любой ошибке
    - Рефлексии
    - Новом знании/инсайте
    """

    LESSONS_DIR = Path("C:/CLI/Pi/lessons")
    TEMPLATE_FILE = Path("C:/CLI/Pi/lessons/templates/lesson_template.md")
    LOG_FILE = Path("C:/CLI/Pi/sessions/auto_lesson_creator.log")

    # Приоритеты
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    def __init__(self):
        self.created: List[Path] = []

    # ============================================================================
    # ОСНОВНЫЕ МЕТОДЫ: Безусловное создание
    # ============================================================================

    def create_lesson_from_error(
        self,
        error_type: str,
        error_message: str,
        context: str = "",
        priority: str = "HIGH"
    ) -> Tuple[bool, Path, str]:
        """
        Создает lesson из ошибки (БЕЗУСЛОВНО).

        Args:
            error_type: Тип ошибки (EPERM, SYNTAX, LOGIC, etc.)
            error_message: Текст ошибки
            context: Контекст/стек вызовов
            priority: CRITICAL/HIGH/MEDIUM/LOW

        Returns:
            (success, file_path, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H%M%S")

        # Формируем имя файла
        safe_error = "".join(c if c.isalnum() else "_" for c in error_type)[:20]
        filename = f"lesson_{today}_ERROR_{safe_error}_{timestamp}.md"
        filepath = self.LESSONS_DIR / filename

        # Создаем контент
        content = self._build_error_lesson(
            date=today,
            error_type=error_type,
            error_message=error_message,
            context=context,
            priority=priority
        )

        return self._write_lesson(filepath, content)

    def create_lesson_from_reflection(
        self,
        topic: str,
        insight: str,
        application: str = "",
        priority: str = "MEDIUM"
    ) -> Tuple[bool, Path, str]:
        """
        Создает lesson из рефлексии/инсайта (БЕЗУСЛОВНО).

        Args:
            topic: Тема урока
            insight: Инсайт/открытие
            application: Как применять
            priority: CRITICAL/HIGH/MEDIUM/LOW

        Returns:
            (success, file_path, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H%M%S")

        # Формируем имя файла
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:20]
        filename = f"lesson_{today}_REFL_{safe_topic}_{timestamp}.md"
        filepath = self.LESSONS_DIR / filename

        # Создаем контент
        content = self._build_reflection_lesson(
            date=today,
            topic=topic,
            insight=insight,
            application=application,
            priority=priority
        )

        return self._write_lesson(filepath, content)

    def create_lesson_from_knowledge(
        self,
        topic: str,
        knowledge: str,
        source: str = "",
        priority: str = "LOW"
    ) -> Tuple[bool, Path, str]:
        """
        Создает lesson из нового знания (БЕЗУСЛОВНО).

        Args:
            topic: Тема
            knowledge: Новое знание
            source: Источник
            priority: CRITICAL/HIGH/MEDIUM/LOW

        Returns:
            (success, file_path, message)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H%M%S")

        # Формируем имя файла
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:20]
        filename = f"lesson_{today}_KNOW_{safe_topic}_{timestamp}.md"
        filepath = self.LESSONS_DIR / filename

        # Создаем контент
        content = self._build_knowledge_lesson(
            date=today,
            topic=topic,
            knowledge=knowledge,
            source=source,
            priority=priority
        )

        return self._write_lesson(filepath, content)

    # ============================================================================
    # СПЕЦИАЛИЗИРОВАННЫЕ МЕТОДЫ
    # ============================================================================

    def create_eperm_lesson(self, file_path: str, resolution: str) -> Tuple[bool, Path, str]:
        """Создает lesson после EPERM ошибки"""
        return self.create_lesson_from_error(
            error_type="EPERM",
            error_message=f"Access denied: {file_path}",
            context=f"File: {file_path}, Resolution: {resolution}",
            priority=self.HIGH
        )

    def create_path_error_lesson(self, command: str, error: str) -> Tuple[bool, Path, str]:
        """Создает lesson после ошибки пути"""
        return self.create_lesson_from_error(
            error_type="PATH_VIOLATION",
            error_message=error,
            context=f"Command: {command}",
            priority=self.CRITICAL
        )

    def create_validation_lesson(self, claim: str, check_type: str) -> Tuple[bool, Path, str]:
        """Создает lesson после нарушения валидации (PoS, Honest, etc.)"""
        return self.create_lesson_from_error(
            error_type=f"VALIDATION_{check_type}",
            error_message=f"Validation failed for: {claim[:100]}",
            context=f"Check type: {check_type}",
            priority=self.CRITICAL
        )

    # ============================================================================
    # ГЕНЕРАТОРЫ КОНТЕНТА
    # ============================================================================

    def _build_error_lesson(
        self,
        date: str,
        error_type: str,
        error_message: str,
        context: str,
        priority: str
    ) -> str:
        """Строит контент lesson для ошибки"""
        metadata = {
            "date": date,
            "topic": f"Ошибка: {error_type}",
            "priority": priority,
            "type": "error",
            "tags": ["error", error_type.lower(), "auto-created"]
        }

        content = f"""---
{json.dumps(metadata, ensure_ascii=False, indent=2)}
---

# Урок: Ошибка {error_type}

**Дата:** {date}
**Сессия:** {self._get_session_link()}
**Тип:** Ошибка
**Приоритет:** {priority}

---

## Контекст

{context[:500] if context else "Контекст не указан"}

---

## Ошибка

```
{error_message[:1000]}
```

---

## Root Cause Analysis (5 Why's)

1. Почему произошла ошибка? → [заполнить]
2. Почему? → [заполнить]
3. Почему? → [заполнить]
4. Почему? → [заполнить]
5. Почему? → [корневая причина]

---

## Вывод/Протокол

- [ ] Обновить соответствующий .md файл правил
- [ ] Добавить проверку/блокировку в gatekeeper.py
- [ ] Протестировать сценарий

**Протокол:** [что делать в будущем]

---

## Метаданные

**Создано:** Автоматически (auto_lesson_creator.py)
**Теги:** error, {error_type.lower()}, auto-created
"""
        return content

    def _build_reflection_lesson(
        self,
        date: str,
        topic: str,
        insight: str,
        application: str,
        priority: str
    ) -> str:
        """Строит контент lesson для рефлексии"""
        metadata = {
            "date": date,
            "topic": topic,
            "priority": priority,
            "type": "reflection",
            "tags": ["reflection", "insight", "auto-created"]
        }

        content = f"""---
{json.dumps(metadata, ensure_ascii=False, indent=2)}
---

# Урок: {topic}

**Дата:** {date}
**Сессия:** {self._get_session_link()}
**Тип:** Рефлексия/Инсайт
**Приоритет:** {priority}

---

## Контекст

Процесс работы над задачей.

---

## Инсайт

{insight[:1000]}

---

## Применение

{application[:500] if application else "Как применить это знание:"}

1. [шаг 1]
2. [шаг 2]
3. [шаг 3]

---

## Вывод/Протокол

**Протокол:** [что делать в будущем]

---

## Метаданные

**Создано:** Автоматически (auto_lesson_creator.py)
**Теги:** reflection, insight, auto-created
"""
        return content

    def _build_knowledge_lesson(
        self,
        date: str,
        topic: str,
        knowledge: str,
        source: str,
        priority: str
    ) -> str:
        """Строит контент lesson для нового знания"""
        metadata = {
            "date": date,
            "topic": topic,
            "priority": priority,
            "type": "knowledge",
            "tags": ["knowledge", "reference", "auto-created"]
        }

        content = f"""---
{json.dumps(metadata, ensure_ascii=False, indent=2)}
---

# Знание: {topic}

**Дата:** {date}
**Сессия:** {self._get_session_link()}
**Тип:** Знание
**Приоритет:** {priority}

---

## Содержание

{knowledge[:1000]}

---

## Источник

{source if source else "Источник не указан"}

---

## Применение

- [ ] Когда использовать
- [ ] Как интегрировать в процессы

---

## Метаданные

**Создано:** Автоматически (auto_lesson_creator.py)
**Теги:** knowledge, reference, auto-created
"""
        return content

    # ============================================================================
    # УТИЛИТЫ
    # ============================================================================

    def _write_lesson(self, filepath: Path, content: str) -> Tuple[bool, Path, str]:
        """Записывает lesson файл"""
        try:
            # Создаем директорию если нужно
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Пишем файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.created.append(filepath)
            self._log_creation(filepath, "SUCCESS")

            return True, filepath, f"Lesson создан: {filepath.name}"

        except Exception as e:
            self._log_creation(str(filepath), f"FAILED: {e}")
            return False, filepath, f"Ошибка создания lesson: {e}"

    def _get_session_link(self) -> str:
        """Возвращает ссылку на текущую сессию"""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"sessions/{today}_session.log"

    def _log_creation(self, filepath: Path, status: str):
        """Логирует создание"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "LESSON_CREATED" if status == "SUCCESS" else "LESSON_FAILED",
            "file": str(filepath),
            "status": status
        }

        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def get_today_lessons(self) -> List[Path]:
        """Возвращает список lesson за сегодня"""
        today = datetime.now().strftime("%Y-%m-%d")
        return list(self.LESSONS_DIR.glob(f"lesson_{today}_*.md"))


# Глобальный экземпляр
_creator_instance: Optional[AutoLessonCreator] = None


def get_creator() -> AutoLessonCreator:
    """Возвращает (или создает) глобальный экземпляр AutoLessonCreator"""
    global _creator_instance
    if _creator_instance is None:
        _creator_instance = AutoLessonCreator()
    return _creator_instance


def lesson_from_error(error_type: str, error_message: str, context: str = "", priority: str = "HIGH") -> Tuple[bool, Path, str]:
    """
    Создает lesson из ошибки (БЕЗУСЛОВНО).
    Не задает вопросов, не требует подтверждения.
    """
    return get_creator().create_lesson_from_error(error_type, error_message, context, priority)


def lesson_from_reflection(topic: str, insight: str, application: str = "", priority: str = "MEDIUM") -> Tuple[bool, Path, str]:
    """
    Создает lesson из рефлексии (БЕЗУСЛОВНО).
    Не задает вопросов, не требует подтверждения.
    """
    return get_creator().create_lesson_from_reflection(topic, insight, application, priority)


def lesson_from_knowledge(topic: str, knowledge: str, source: str = "", priority: str = "LOW") -> Tuple[bool, Path, str]:
    """
    Создает lesson из знания (БЕЗУСЛОВНО).
    Не задает вопросов, не требует подтверждения.
    """
    return get_creator().create_lesson_from_knowledge(topic, knowledge, source, priority)


# CLI для тестирования
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto Lesson Creator V3 — Безусловная запись уроков")
    parser.add_argument('--type', choices=['error', 'reflection', 'knowledge'], required=True, help='Тип урока')
    parser.add_argument('--topic', required=True, help='Тема/тип ошибки')
    parser.add_argument('--content', required=True, help='Содержание (ошибка/инсайт/знание)')
    parser.add_argument('--context', default='', help='Контекст')
    parser.add_argument('--priority', choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], default='MEDIUM', help='Приоритет')

    args = parser.parse_args()

    creator = get_creator()

    if args.type == 'error':
        success, path, message = creator.create_lesson_from_error(
            args.topic, args.content, args.context, args.priority
        )
    elif args.type == 'reflection':
        success, path, message = creator.create_lesson_from_reflection(
            args.topic, args.content, args.context, args.priority
        )
    elif args.type == 'knowledge':
        success, path, message = creator.create_lesson_from_knowledge(
            args.topic, args.content, args.context, args.priority
        )
    else:
        print("Неизвестный тип")
        sys.exit(1)

    print(f"Success: {success}")
    print(f"Message: {message}")
    if success:
        print(f"Path: {path}")
        print(f"\nФайл создан автоматически. БЕЗУСЛОВНО.")
