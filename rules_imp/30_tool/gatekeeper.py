#!/usr/bin/env python3
"""
GATEKEEPER V3 — Центральный Контроллер Блокировок
Проверяет соблюдение критических правил перед действиями

Версия: 3.0
Дата: 2026-03-30
Приоритет: КРИТИЧЕСКИЙ
"""

import sys
import json
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any


class GatekeeperError(Exception):
    """Исключение при нарушении правил Gatekeeper"""
    pass


class Gatekeeper:
    """
    Главный контроллер блокировок V3.
    Проверяет PoS, honest reporting, code accuracy и другие критические правила.
    """

    # Конфигурация
    VIOLATIONS_LOG = Path("C:/CLI/Pi/sessions/gatekeeper_violations.log")
    APPROVALS_LOG = Path("C:/CLI/Pi/sessions/gatekeeper_approvals.log")

    def __init__(self):
        self.violations: List[Dict] = []
        self.context: Dict[str, Any] = {}

    # ============================================================================
    # ПРОВЕРКА 1: Proof of Search (Принцип IV)
    # ============================================================================

    def require_proof_of_search(self, claim: str, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Требует PoS для утверждений о коде/данных.

        Args:
            claim: Утверждение (например, "Функция X определена в файле Y")
            file_path: Путь к файлу, если есть

        Returns:
            (allowed, message)
        """
        # Проверяем, содержит ли claim упоминание о коде/файлах
        code_indicators = [
            r'\bфункция\s+\w+',
            r'\bкласс\s+\w+',
            r'\bфайл\s+[\w\./\\]+',
            r'\bв\s+файле\s+[\w\./\\]+',
            r'\bопределена\s+в\b',
            r'\bнаходится\s+в\b',
            r'\bсодержит\b',
        ]

        is_code_claim = any(re.search(pattern, claim, re.IGNORECASE) for pattern in code_indicators)

        if not is_code_claim:
            return True, "Не требует PoS (нет утверждений о коде)"

        # Проверяем наличие PoS в claim
        pos_indicators = [
            r'rg\s+-\w+\s+"',
            r'Proof\s+of\s+Search',
            r'поиск\s+выполнен',
            r'данные\s+взяты\s+из',
            r'string:\s*\d+',
        ]

        has_pos = any(re.search(pattern, claim, re.IGNORECASE) for pattern in pos_indicators)

        if not has_pos:
            error_msg = (
                f"[GATEKEEPER BLOCKED] Утверждение требует Proof of Search:\n"
                f"'{claim[:80]}...'\n\n"
                f"Добавьте:\n"
                f"- Команду поиска: rg -nH 'термин' путь\n"
                f"- Файл и строку\n"
                f"- Прямую цитату\n"
                f"- Вердикт: 'Данные взяты из исходника'"
            )
            self._log_violation("PROOF_OF_SEARCH_REQUIRED", claim, error_msg)
            return False, error_msg

        return True, "PoS подтвержден"

    # ============================================================================
    # ПРОВЕРКА 2: Honest Reporting (Принцип I)
    # ============================================================================

    def require_honest_reporting(self, status: str, total: Optional[int] = None, completed: Optional[int] = None) -> Tuple[bool, str]:
        """
        Требует честного отчета (X из Y) для частичного выполнения.

        Args:
            status: Текст статуса ("выполнено", "готово", etc.)
            total: Общее количество
            completed: Выполненное количество

        Returns:
            (allowed, message)
        """
        # Проверяем декларативные утверждения
        vague_terms = [
            r'\bвыполнено\b(?!\s*:\s*\d+\s*из\s*\d+)',
            r'\bготово\b(?!\s*:\s*\d+\s*из\s*\d+)',
            r'\bпочти\s+вс[её]\b',
            r'\bбольшинство\b',
            r'\bпроверено\b(?!\s*по\s*правилам.*:\s*\d+)',
            r'\bзавершено\b(?!\s*:\s*\d+\s*из\s*\d+)',
        ]

        has_vague = any(re.search(pattern, status, re.IGNORECASE) for pattern in vague_terms)

        if has_vague and (total is None or completed is None):
            error_msg = (
                f"[GATEKEEPER BLOCKED] Требуется честный отчет (X из Y)\n"
                f"Статус: '{status}'\n\n"
                f"Запрещено: 'выполнено', 'готово', 'почти всё' без X/Y\n"
                f"Обязательно: 'Выполнено: {completed or 'X'} из {total or 'Y'} (Z%)'\n\n"
                f"Пример:\n"
                f"'Выполнено: 7 из 10 задач (70%)\n"
                f" Выполненные: [...]\n"
                f" Невыполненные: [...]'"
            )
            self._log_violation("HONEST_REPORTING_REQUIRED", status, error_msg)
            return False, error_msg

        return True, "Честный отчет подтвержден"

    # ============================================================================
    # ПРОВЕРКА 3: Code Accuracy (Принцип II)
    # ============================================================================

    def require_code_accuracy(self, code: str, language: str = 'python') -> Tuple[bool, str]:
        """
        Проверяет синтаксическую корректность кода.

        Args:
            code: Исходный код
            language: Язык программирования

        Returns:
            (allowed, message)
        """
        if language.lower() == 'python':
            try:
                ast.parse(code)
                return True, "Синтаксис Python корректен"
            except SyntaxError as e:
                error_msg = (
                    f"[GATEKEEPER BLOCKED] Синтаксическая ошибка в Python:\n"
                    f"{e}\n\n"
                    f"Исправьте код перед записью."
                )
                self._log_violation("SYNTAX_ERROR", code[:100], str(e))
                return False, error_msg

        # Для других языков — делегировать внешним инструментам
        return True, f"Проверка {language} делегирована"

    # ============================================================================
    # ПРОВЕРКА 4: Path Validation (V3)
    # ============================================================================

    def validate_path(self, path: str, context: str = 'bash') -> Tuple[bool, str, Optional[str]]:
        """
        Проверяет путь на соответствие правилам path.md.

        Args:
            path: Путь для проверки
            context: Контекст (bash, json, markdown, bat)

        Returns:
            (is_valid, message, corrected_path)
        """
        errors = []
        corrected = path

        if context == 'bash':
            # Проверка 1: Обратные слеши
            if '\\' in path:
                errors.append("Обратный слеш (\\) в bash. Используйте: /")
                corrected = corrected.replace('\\', '/')

            # Проверка 2: @ в имени файла
            if re.search(r'/(?!@)[^/]*@[^/]*\.\w+', path) or path.startswith('@'):
                errors.append("@ в имени файла. @ — триггер, не часть имени")

            # Проверка 3: Пробелы без кавычек
            if ' ' in path and not (path.startswith('"') or path.startswith("'")):
                errors.append(f"Пробелы в пути '{path}' требуют кавычек")

        if errors:
            error_msg = "\n".join(f"- {e}" for e in errors)
            full_msg = f"[GATEKEEPER BLOCKED] Неверный путь:\n{error_msg}"
            self._log_violation("PATH_VIOLATION", path, error_msg)
            return False, full_msg, corrected if corrected != path else None

        return True, "Путь корректен", None

    # ============================================================================
    # ПРОВЕРКА 5: Lesson Requirement (V3)
    # ============================================================================

    def require_lesson_for_session(self) -> Tuple[bool, str]:
        """
        Проверяет наличие lesson перед открытием сессии.

        Returns:
            (allowed, message)
        """
        lessons_dir = Path("C:/CLI/Pi/lessons")
        today = datetime.now().strftime("%Y-%m-%d")

        # Ищем сегодняшние уроки
        today_lessons = list(lessons_dir.glob(f"lesson_{today}_*.md"))

        if not today_lessons:
            error_msg = (
                f"[GATEKEEPER BLOCKED] Сессия не может быть открыта\n"
                f"Требование: Создать lesson в C:/CLI/Pi/lessons/\n\n"
                f"Формат: lesson_YYYY-MM-DD_[тема].md\n"
                f"С JSON-метаданными в начале файла\n\n"
                f"Создайте lesson и повторите попытку."
            )
            self._log_violation("LESSON_REQUIRED", "session_start", "No lesson found")
            return False, error_msg

        # Проверяем валидность метаданных
        for lesson in today_lessons:
            if self._has_valid_metadata(lesson):
                return True, f"Lesson найден: {lesson.name}"

        error_msg = (
            f"[GATEKEEPER BLOCKED] Lesson найден, но без валидных метаданных\n"
            f"Требуется JSON в начале файла между ---"
        )
        return False, error_msg

    def _has_valid_metadata(self, lesson_file: Path) -> bool:
        """Проверяет наличие JSON-метаданных в lesson"""
        try:
            content = lesson_file.read_text(encoding='utf-8')
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if match:
                json.loads(match.group(1).strip())
                return True
        except:
            pass
        return False

    # ============================================================================
    # Логирование
    # ============================================================================

    def _log_violation(self, violation_type: str, original: str, message: str):
        """Логирует нарушение"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "VIOLATION",
            "violation_type": violation_type,
            "original": original[:100],
            "message": message[:200]
        }

        self.VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(self.VIOLATIONS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        self.violations.append(entry)

    def _log_approval(self, check_type: str, details: str):
        """Логирует успешную проверку"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "APPROVAL",
            "check_type": check_type,
            "details": details[:100]
        }

        with open(self.APPROVALS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # ============================================================================
    # Комплексные Проверки
    # ============================================================================

    def before_file_write(self, file_path: str, content: str) -> Tuple[bool, str]:
        """
        Комплексная проверка перед записью файла.

        Returns:
            (allowed, message)
        """
        # Проверка 1: Путь
        valid, msg, corrected = self.validate_path(file_path)
        if not valid:
            return False, msg

        # Проверка 2: Синтаксис кода (если это Python)
        if file_path.endswith('.py'):
            valid, msg = self.require_code_accuracy(content)
            if not valid:
                return False, msg

        self._log_approval("FILE_WRITE", f"Path: {file_path}")
        return True, "Все проверки пройдены"

    def before_completion_report(self, status_text: str) -> Tuple[bool, str]:
        """
        Проверка перед отчетом о завершении.
        """
        return self.require_honest_reporting(status_text)


# Глобальный экземпляр
_gatekeeper_instance: Optional[Gatekeeper] = None


def get_gatekeeper() -> Gatekeeper:
    """Возвращает (или создает) глобальный экземпляр Gatekeeper"""
    global _gatekeeper_instance
    if _gatekeeper_instance is None:
        _gatekeeper_instance = Gatekeeper()
    return _gatekeeper_instance


def require_proof_of_search(claim: str, file_path: Optional[str] = None) -> Tuple[bool, str]:
    """Удобная функция для требования PoS"""
    return get_gatekeeper().require_proof_of_search(claim, file_path)


def require_honest_reporting(status: str, total: Optional[int] = None, completed: Optional[int] = None) -> Tuple[bool, str]:
    """Удобная функция для требования честного отчета"""
    return get_gatekeeper().require_honest_reporting(status, total, completed)


def validate_path(path: str, context: str = 'bash') -> Tuple[bool, str, Optional[str]]:
    """Удобная функция для валидации пути"""
    return get_gatekeeper().validate_path(path, context)


def check_session_allowed() -> Tuple[bool, str]:
    """Удобная функция для проверки сессии"""
    return get_gatekeeper().require_lesson_for_session()


def require_code_accuracy(code: str, language: str = 'python') -> Tuple[bool, str]:
    """Удобная функция для проверки кода"""
    return get_gatekeeper().require_code_accuracy(code, language)


def before_file_write(file_path: str, content: str) -> Tuple[bool, str]:
    """Удобная функция комплексной проверки перед записью"""
    return get_gatekeeper().before_file_write(file_path, content)


# CLI для тестирования
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gatekeeper V3 — Контроллер блокировок")
    parser.add_argument('--check', choices=['pos', 'honest', 'path', 'session'], help='Тип проверки')
    parser.add_argument('--value', help='Значение для проверки')

    args = parser.parse_args()

    g = get_gatekeeper()

    if args.check == 'pos':
        result = g.require_proof_of_search(args.value or "Функция x в файле y")
    elif args.check == 'honest':
        result = g.require_honest_reporting(args.value or "Выполнено")
    elif args.check == 'path':
        result = g.validate_path(args.value or "C:\\path\\file")
    elif args.check == 'session':
        result = g.require_lesson_for_session()
    else:
        print("Использование: gatekeeper.py --check {pos|honest|path|session} --value '...'")
        sys.exit(1)

    allowed, message = result[0], result[1]
    print(f"Allowed: {allowed}")
    print(f"Message: {message}")
    sys.exit(0 if allowed else 1)
