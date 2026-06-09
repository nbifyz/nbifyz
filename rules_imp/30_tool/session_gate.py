#!/usr/bin/env python3
"""
SESSION GATE V3 — Блокиратор Сессий Без Урока
Проверяет наличие валидного lesson перед открытием сессии

Версия: 3.0
Дата: 2026-03-30
Приоритет: КРИТИЧЕСКИЙ
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any


class SessionGateError(Exception):
    """Исключение при блокировке сессии"""
    pass


class SessionGate:
    """
    Блокиратор сессий V3.
    Без валидного lesson — сессия не открывается.
    """

    LESSONS_DIR = Path("C:/CLI/Pi/lessons")
    SESSIONS_DIR = Path("C:/CLI/Pi/sessions")
    BLOCKS_LOG = Path("C:/CLI/Pi/sessions/session_blocks.log")
    APPROVALS_LOG = Path("C:/CLI/Pi/sessions/session_approvals.log")

    def __init__(self):
        self.blocks: List[Dict] = []

    # ============================================================================
    # ОСНОВНАЯ ПРОВЕРКА: Перед открытием сессии
    # ============================================================================

    def check_session_allowed(self) -> Tuple[bool, str, Optional[Path]]:
        """
        Проверяет, можно ли открыть сессию.

        Returns:
            (allowed, message, lesson_path)
            - allowed: True если сессию можно открыть
            - message: Сообщение пользователю
            - lesson_path: Путь к найденному lesson (если allowed=True)
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # Проверка 1: Существует ли директория lessons
        if not self.LESSONS_DIR.exists():
            error_msg = (
                f"[SESSION GATE BLOCKED] Директория уроков не существует\n"
                f"Путь: {self.LESSONS_DIR}\n\n"
                f"Создайте директорию и lesson файл."
            )
            self._log_block("LESSONS_DIR_MISSING", str(self.LESSONS_DIR), "Directory does not exist")
            return False, error_msg, None

        # Проверка 2: Есть ли lesson за сегодня
        today_lessons = list(self.LESSONS_DIR.glob(f"lesson_{today}_*.md"))

        if not today_lessons:
            error_msg = (
                f"[SESSION GATE BLOCKED] Сессия не может быть открыта\n"
                f"Причина: Нет lesson за {today}\n\n"
                f"Требование: Создать lesson в {self.LESSONS_DIR}\n"
                f"Формат: lesson_{today}_[тема].md\n\n"
                f"Файл должен содержать JSON-метаданные в начале:\n"
                f"---\n"
                f'{{"date": "{today}", "topic": "тема", "priority": "CRITICAL|HIGH|MEDIUM|LOW"}}\n'
                f"---\n\n"
                f"Создайте lesson и повторите попытку."
            )
            self._log_block("LESSON_REQUIRED", f"lesson_{today}_*.md", "No lesson for today")
            return False, error_msg, None

        # Проверка 3: Валидны ли метаданные уроков
        valid_lessons = []
        for lesson in today_lessons:
            if self._has_valid_metadata(lesson):
                valid_lessons.append(lesson)

        if not valid_lessons:
            error_msg = (
                f"[SESSION GATE BLOCKED] Lesson найден, но без валидных метаданных\n"
                f"Найдено файлов: {len(today_lessons)}\n\n"
                f"Требуется JSON в начале файла между ---\n"
                f"Пример:\n"
                f"---\n"
                f'{{"date": "{today}", "topic": "Название", "priority": "HIGH"}}\n'
                f"---"
            )
            self._log_block("METADATA_INVALID", str(today_lessons[0]), "Invalid or missing JSON metadata")
            return False, error_msg, None

        # Выбираем lesson с наивысшим приоритетом
        selected_lesson = self._select_lesson_by_priority(valid_lessons)

        self._log_approval("SESSION_ALLOWED", str(selected_lesson))
        return True, f"Сессия разрешена. Lesson: {selected_lesson.name}", selected_lesson

    def _has_valid_metadata(self, lesson_file: Path) -> bool:
        """
        Проверяет наличие валидных JSON-метаданных в lesson.

        Args:
            lesson_file: Путь к файлу lesson

        Returns:
            True если есть валидный JSON между ---
        """
        try:
            content = lesson_file.read_text(encoding='utf-8')
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                metadata = json.loads(match.group(1).strip())
                # Проверяем обязательные поля
                required_fields = ['date', 'topic']
                return all(field in metadata for field in required_fields)
        except json.JSONDecodeError:
            pass
        except Exception:
            pass
        return False

    def _select_lesson_by_priority(self, lessons: List[Path]) -> Path:
        """
        Выбирает lesson с наивысшим приоритетом.

        Priority: CRITICAL > HIGH > MEDIUM > LOW
        """
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, '': 0}

        best_lesson = lessons[0]
        best_priority = 0

        for lesson in lessons:
            try:
                content = lesson.read_text(encoding='utf-8')
                match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    metadata = json.loads(match.group(1).strip())
                    priority = metadata.get('priority', '')
                    priority_value = priority_order.get(priority, 0)

                    if priority_value > best_priority:
                        best_priority = priority_value
                        best_lesson = lesson
            except:
                pass

        return best_lesson

    def get_lesson_metadata(self, lesson_path: Path) -> Optional[Dict[str, Any]]:
        """
        Извлекает метаданные из lesson файла.

        Args:
            lesson_path: Путь к lesson

        Returns:
            Словарь с метаданными или None
        """
        try:
            content = lesson_path.read_text(encoding='utf-8')
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
        except:
            pass
        return None

    # ============================================================================
    # Логирование
    # ============================================================================

    def _log_block(self, block_type: str, original: str, reason: str):
        """Логирует блокировку сессии"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SESSION_BLOCKED",
            "block_type": block_type,
            "original": original[:100],
            "reason": reason[:200]
        }

        self.BLOCKS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(self.BLOCKS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        self.blocks.append(entry)

    def _log_approval(self, check_type: str, details: str):
        """Логирует успешную проверку"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "SESSION_APPROVED",
            "check_type": check_type,
            "details": details[:100]
        }

        with open(self.APPROVALS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# Глобальный экземпляр
_session_gate_instance: Optional[SessionGate] = None


def get_session_gate() -> SessionGate:
    """Возвращает (или создает) глобальный экземпляр SessionGate"""
    global _session_gate_instance
    if _session_gate_instance is None:
        _session_gate_instance = SessionGate()
    return _session_gate_instance


def check_session() -> Tuple[bool, str, Optional[Path]]:
    """
    Главная функция для проверки сессии.
    Используйте перед открытием любой сессии.

    Returns:
        (allowed, message, lesson_path)
    """
    return get_session_gate().check_session_allowed()


def get_current_lesson() -> Optional[Path]:
    """
    Возвращает путь к текущему lesson за сегодня.

    Returns:
        Path к lesson или None если нет валидного lesson
    """
    allowed, _, lesson_path = get_session_gate().check_session_allowed()
    return lesson_path if allowed else None


# CLI для тестирования
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Session Gate V3 — Блокиратор сессий")
    parser.add_argument('--check', action='store_true', help='Проверить можно ли открыть сессию')
    parser.add_argument('--get-lesson', action='store_true', help='Получить путь к текущему lesson')

    args = parser.parse_args()

    gate = get_session_gate()

    if args.check or (not args.get_lesson):
        allowed, message, lesson_path = gate.check_session_allowed()
        print(f"Session Allowed: {allowed}")
        print(f"Message: {message}")
        if lesson_path:
            print(f"Lesson: {lesson_path}")
            metadata = gate.get_lesson_metadata(lesson_path)
            if metadata:
                print(f"Metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        sys.exit(0 if allowed else 1)

    elif args.get_lesson:
        lesson = get_current_lesson()
        if lesson:
            print(f"Current lesson: {lesson}")
            metadata = gate.get_lesson_metadata(lesson)
            if metadata:
                print(f"Metadata: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        else:
            print("No valid lesson found")
            sys.exit(1)
