#!/usr/bin/env python3
"""
PRE-RUN VALIDATOR V3 — Валидатор Команд Перед Выполнением
Перехватывает команды bash и блокирует неверные пути

Версия: 3.0
Дата: 2026-03-30
Приоритет: КРИТИЧЕСКИЙ
"""

import sys
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any


class PreRunValidatorError(Exception):
    """Исключение при нарушении правил валидации"""
    pass


class PreRunValidator:
    """
    Валидатор команд перед выполнением в bash.
    Проверяет пути, форматы, блокирует опасные команды.
    """

    VIOLATIONS_LOG = Path("C:/CLI/Pi/sessions/prerun_violations.log")
    APPROVALS_LOG = Path("C:/CLI/Pi/sessions/prerun_approvals.log")

    def __init__(self):
        self.violations: List[Dict] = []

    # ============================================================================
    # ОСНОВНАЯ ПРОВЕРКА: Перед отправкой в bash
    # ============================================================================

    def validate_bash_command(self, command: str) -> Tuple[bool, str, Optional[str]]:
        """
        Проверяет команду перед отправкой в bash.

        Args:
            command: Команда для bash

        Returns:
            (is_valid, message, corrected_command)
        """
        errors = []
        corrected = command

        # ПРОВЕРКА 1: Обратные слеши в путях без кавычек
        # Находим пути с \ вне кавычек
        backslash_patterns = [
            r'[a-zA-Z]:\\\w+',  # C:\path
            r'"[^"]*[a-zA-Z]:\\',  # "C:\...
        ]

        for pattern in backslash_patterns:
            if re.search(pattern, command):
                errors.append("Обратный слеш (\\) в bash. Используйте: /")
                corrected = corrected.replace('\\', '/')
                break

        # ПРОВЕРКА 2: @ в имени файла (не путать с триггером)
        # Проверяем, что @ не используется как часть имени файла
        at_in_filename = re.search(r'\s[@\w]+@[^\s\'\"]+', command)
        if at_in_filename and not self._is_valid_trigger_usage(command):
            errors.append("@ в имени файла. @ — триггер, не часть имени")

        # ПРОВЕРКА 3: Пробелы в путях без кавычек
        # Находим пути с пробелами без кавычек
        unquoted_spaces = self._find_unquoted_spaces(command)
        if unquoted_spaces:
            errors.append(f"Пробелы в пути требуют кавычек: {unquoted_spaces}")
            corrected = self._quote_paths_with_spaces(corrected)

        # ПРОВЕРКА 4: Опасные команды
        dangerous = self._check_dangerous_commands(command)
        if dangerous:
            errors.append(f"Опасная команда: {dangerous}")

        if errors:
            error_msg = "\n".join(f"- {e}" for e in errors)
            full_msg = f"[PRE-RUN BLOCKED] Команда заблокирована:\n{error_msg}\n\nИсправленная:\n{corrected}"
            self._log_violation("BASH_VALIDATION_FAILED", command, error_msg)
            return False, full_msg, corrected if corrected != command else None

        self._log_approval("BASH_COMMAND", command[:100])
        return True, "Команда валидна", None

    def _is_valid_trigger_usage(self, command: str) -> bool:
        """Проверяет, что @ используется как триггер, а не часть имени"""
        # Триггеры используются отдельно или в начале слова
        valid_patterns = [
            r'^@',  # @ в начале
            r'\s@',  # Пробел перед @
        ]
        return any(re.search(p, command) for p in valid_patterns)

    def _find_unquoted_spaces(self, command: str) -> List[str]:
        """Находит пути с пробелами вне кавычек"""
        issues = []
        # Разбиваем на токены (очень упрощенно)
        tokens = command.split()
        for token in tokens:
            # Если токен содержит пробелы (после разбивки это части пути)
            # и не начинается с кавычки
            if ' ' in token and not (token.startswith('"') or token.startswith("'")):
                if '/' in token or '\\' in token or ':' in token:
                    issues.append(token)
        return issues

    def _quote_paths_with_spaces(self, command: str) -> str:
        """Добавляет кавычки к путям с пробелами"""
        # Упрощенная реализация - в реальности может потребоваться
        # более сложная логика с учетом уже существующих кавычек
        tokens = command.split()
        corrected_tokens = []
        for token in tokens:
            if ' ' in token and '/' in token and not (token.startswith('"') or token.startswith("'")):
                corrected_tokens.append(f'"{token}"')
            else:
                corrected_tokens.append(token)
        return ' '.join(corrected_tokens)

    def _check_dangerous_commands(self, command: str) -> Optional[str]:
        """Проверяет наличие опасных команд"""
        dangerous_patterns = [
            (r'rm\s+-rf\s+/', 'rm -rf /'),
            (r'>\s*/dev/null.*2>&1.*rm', 'перенаправление вывода перед rm'),
            (r'mkfs', 'mkfs'),
            (r'dd\s+if=.*of=/dev', 'dd в системное устройство'),
            (r':\(\)\{\s*:\|:&\};:', 'fork bomb'),
        ]

        for pattern, description in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return description
        return None

    # ============================================================================
    # ПРОВЕРКА JSON Path (для tool calls)
    # ============================================================================

    def validate_json_path(self, path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Проверяет путь для JSON (tool calls).
        В JSON должны быть двойные обратные слеши.

        Args:
            path: Путь из JSON

        Returns:
            (is_valid, message, corrected_path)
        """
        # В JSON пути должны иметь \\, а не /
        if '/' in path and not '\\' in path and ':' in path:
            # Это Windows путь с прямыми слешами в JSON - ошибка
            corrected = path.replace('/', '\\\\')
            error_msg = (
                f"[PRE-RUN BLOCKED] JSON path требует \\\\\\\\ (двойные слеши)\n"
                f"Получено: {path}\n"
                f"Должно быть: {corrected}"
            )
            self._log_violation("JSON_PATH_INVALID", path, "Needs double backslashes")
            return False, error_msg, corrected

        self._log_approval("JSON_PATH", path)
        return True, "Путь корректен для JSON", None

    # ============================================================================
    # Авто-исправление
    # ============================================================================

    def auto_correct_bash_path(self, path: str) -> str:
        """
        Автоматически исправляет путь для bash.

        Args:
            path: Исходный путь

        Returns:
            Исправленный путь
        """
        corrected = path

        # Заменяем \ на /
        if '\\' in corrected:
            corrected = corrected.replace('\\', '/')

        # Добавляем кавычки если есть пробелы
        if ' ' in corrected and not (corrected.startswith('"') or corrected.startswith("'")):
            corrected = f'"{corrected}"'

        return corrected

    # ============================================================================
    # Логирование
    # ============================================================================

    def _log_violation(self, violation_type: str, original: str, message: str):
        """Логирует нарушение"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "VIOLATION",
            "violation_type": violation_type,
            "original": original[:200],
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


# Глобальный экземпляр
_validator_instance: Optional[PreRunValidator] = None


def get_validator() -> PreRunValidator:
    """Возвращает (или создает) глобальный экземпляр PreRunValidator"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = PreRunValidator()
    return _validator_instance


def before_bash(command: str) -> Tuple[bool, str, Optional[str]]:
    """
    Главная функция для проверки перед отправкой в bash.
    Используйте эту функцию как pre-run hook.

    Returns:
        (allowed, message, corrected_command)
        - allowed: Можно ли выполнять
        - message: Сообщение (ошибка или подтверждение)
        - corrected_command: Исправленная команда (если есть)
    """
    return get_validator().validate_bash_command(command)


def validate_json_path(path: str) -> Tuple[bool, str, Optional[str]]:
    """Удобная функция для валидации JSON-пути"""
    return get_validator().validate_json_path(path)


def auto_correct_path(path: str) -> str:
    """Удобная функция для авто-исправления пути"""
    return get_validator().auto_correct_bash_path(path)


# CLI для тестирования
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pre-Run Validator V3")
    parser.add_argument('command', nargs='?', help='Команда для проверки')
    parser.add_argument('--check', choices=['bash', 'json'], default='bash', help='Тип проверки')
    parser.add_argument('--auto-correct', action='store_true', help='Вывести исправленную версию')

    args = parser.parse_args()

    v = get_validator()

    if args.check == 'bash':
        allowed, message, corrected = v.validate_bash_command(args.command or 'echo test')
    elif args.check == 'json':
        allowed, message, corrected = v.validate_json_path(args.command or 'C:/path/to/file')
    else:
        print("Использование: pre_run_validator.py 'команда' --check {bash|json}")
        sys.exit(1)

    print(f"Allowed: {allowed}")
    print(f"Message: {message}")
    if corrected:
        print(f"Corrected: {corrected}")

    if args.auto_correct and corrected:
        print(f"\nИсправленная команда:\n{corrected}")

    sys.exit(0 if allowed else 1)
