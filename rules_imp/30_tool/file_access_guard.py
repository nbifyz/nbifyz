#!/usr/bin/env python3
"""
FILE ACCESS GUARD V3 — Защита от EPERM/EACCES
Автоматически снимает Read-Only атрибут и обрабатывает ошибки доступа

Версия: 3.0
Дата: 2026-03-30
Приоритет: КРИТИЧЕСКИЙ
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any


class FileAccessGuardError(Exception):
    """Исключение при невозможности получить доступ к файлу"""
    pass


class FileAccessGuard:
    """
    Защита от ошибок доступа V3.
    Реализует алгоритм EPERM_REFERENCE.md:
    1. Проверить IsReadOnly
    2. Проверить блокировку процессом
    3. Проверить права доступа
    """

    LOG_FILE = Path("C:/CLI/Pi/sessions/file_access_guard.log")
    EPERM_REF = Path("C:/CLI/Pi/rules_imp/00_core/EPERM_REFERENCE.md")

    def __init__(self):
        self.actions: List[Dict] = []

    # ============================================================================
    # ОСНОВНАЯ ПРОВЕРКА: Перед записью файла
    # ============================================================================

    def before_write_operation(self, file_path: str) -> Tuple[bool, str]:
        """
        Проверяет файл перед операцией записи.

        Args:
            file_path: Путь к файлу

        Returns:
            (can_write, message)
        """
        path = Path(file_path)

        # Если файла нет, проверяем директорию
        if not path.exists():
            parent = path.parent
            if parent.exists():
                self._log_action("FILE_NOT_EXISTS", str(path), "Will create new file")
                return True, "Файл будет создан"
            else:
                return False, f"Директория не существует: {parent}"

        # ШАГ 1: Проверка IsReadOnly
        is_readonly = self._check_readonly(str(path))
        if is_readonly:
            success = self._remove_readonly(str(path))
            if success:
                self._log_action("READONLY_REMOVED", str(path), "IsReadOnly was True, now False")
                return True, "Read-Only атрибут снят"
            else:
                error_msg = f"Не удалось снять Read-Only атрибут: {path}"
                self._log_action("READONLY_REMOVE_FAILED", str(path), error_msg)
                return False, error_msg

        # ШАГ 2: Проверка блокировки процессом
        locked_by = self._check_file_lock(str(path))
        if locked_by:
            error_msg = (
                f"Файл заблокирован процессом: {locked_by}\n"
                f"Закройте процесс и повторите операцию."
            )
            self._log_action("FILE_LOCKED", str(path), locked_by)
            return False, error_msg

        # ШАГ 3: Проверка прав доступа (упрощенно)
        if not self._check_write_permissions(str(path)):
            error_msg = (
                f"Недостаточно прав для записи: {path}\n"
                f"Обратитесь к администратору."
            )
            self._log_action("PERMISSION_DENIED", str(path), "No write permissions")
            return False, error_msg

        self._log_action("WRITE_ALLOWED", str(path), "All checks passed")
        return True, "Запись разрешена"

    # ============================================================================
    # ДИАГНОСТИКА: При получении EPERM
    # ============================================================================

    def diagnose_eperm(self, file_path: str, original_error: str = "") -> Tuple[bool, str, str]:
        """
        Диагностирует и пытается исправить EPERM/EACCES.

        Args:
            file_path: Путь к файлу
            original_error: Текст исходной ошибки

        Returns:
            (fixed, diagnosis, action)
            - fixed: Удалось ли исправить
            - diagnosis: Диагноз проблемы
            - action: Рекомендованное действие
        """
        path = Path(file_path)

        if not path.exists():
            return False, "Файл не существует", "Проверьте путь"

        # Проверка 1: IsReadOnly
        if self._check_readonly(str(path)):
            if self._remove_readonly(str(path)):
                return True, "Файл был в режиме Read-Only", "Атрибут снят автоматически"
            else:
                return False, "Файл в режиме Read-Only", "Снимите вручную через PowerShell"

        # Проверка 2: Блокировка
        locked_by = self._check_file_lock(str(path))
        if locked_by:
            return False, f"Файл заблокирован: {locked_by}", f"Закройте процесс {locked_by}"

        # Проверка 3: Права
        if not self._check_write_permissions(str(path)):
            return False, "Недостаточно прав доступа", "Запустите от администратора или измените права"

        # Неизвестная причина
        self._log_action("EPERM_UNKNOWN", str(path), original_error[:200])
        return False, "Неизвестная причина EPERM", "Обратитесь к администратору"

    # ============================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================================

    def _check_readonly(self, file_path: str) -> bool:
        """Проверяет IsReadOnly атрибут через PowerShell"""
        try:
            cmd = [
                'powershell',
                '-Command',
                f'Get-ItemProperty -Path "{file_path}" | Select-Object -ExpandProperty IsReadOnly'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False
            )
            output = result.stdout.strip().lower()
            return 'true' in output
        except Exception:
            # Fallback: проверяем через pathlib
            try:
                path = Path(file_path)
                # Пытаемся открыть на запись без изменения
                with open(path, 'a'):
                    return False
            except PermissionError:
                return True
            except Exception:
                return False

    def _remove_readonly(self, file_path: str) -> bool:
        """Снимает Read-Only атрибут через PowerShell"""
        try:
            cmd = [
                'powershell',
                '-Command',
                f'Set-ItemProperty -Path "{file_path}" -Name IsReadOnly -Value $false'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_file_lock(self, file_path: str) -> Optional[str]:
        """Проверяет, не заблокирован ли файл процессом"""
        try:
            # Пытаемся открыть файл эксклюзивно
            path = Path(file_path)
            try:
                with open(path, 'r+') as f:
                    # Если открылось, файл не заблокирован
                    pass
                return None
            except PermissionError:
                # Проверяем через handle (если доступно)
                cmd = [
                    'powershell',
                    '-Command',
                    f'Get-Process | Where-Object {{$_.Modules -match "{path.name}"}} | Select-Object -First 1 -ExpandProperty ProcessName'
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=False
                )
                if result.stdout.strip():
                    return result.stdout.strip()
                return "unknown"
            except Exception:
                return None
        except Exception:
            return None

    def _check_write_permissions(self, file_path: str) -> bool:
        """Проверяет права на запись"""
        try:
            path = Path(file_path)
            # Проверяем можно ли открыть на добавление
            with open(path, 'a'):
                pass
            return True
        except PermissionError:
            return False
        except Exception:
            return True  # Если другая ошибка, права могут быть

    # ============================================================================
    # МАССОВЫЕ ОПЕРАЦИИ
    # ============================================================================

    def remove_readonly_recursive(self, directory: str, pattern: str = "*") -> Tuple[int, List[str]]:
        """
        Снимает Read-Only со всех файлов в директории.

        Args:
            directory: Путь к директории
            pattern: Маска файлов (по умолчанию все)

        Returns:
            (count, errors)
        """
        path = Path(directory)
        count = 0
        errors = []

        if not path.exists():
            return 0, [f"Директория не существует: {directory}"]

        try:
            cmd = [
                'powershell',
                '-Command',
                f'Get-ChildItem "{directory}" -File -Recurse | ForEach-Object {{ Set-ItemProperty -Path $_.FullName -Name IsReadOnly -Value $false; $_.FullName }}'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False
            )
            if result.returncode == 0:
                count = len([l for l in result.stdout.strip().split('\n') if l])
            else:
                errors.append(result.stderr)
        except Exception as e:
            errors.append(str(e))

        self._log_action("BULK_READONLY_REMOVED", directory, f"Files: {count}, Errors: {len(errors)}")
        return count, errors

    # ============================================================================
    # Логирование
    # ============================================================================

    def _log_action(self, action_type: str, file_path: str, details: str):
        """Логирует действие"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "file": file_path[:100],
            "details": details[:200]
        }

        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        self.actions.append(entry)

    def open_eperm_reference(self):
        """Возвращает путь к EPERM_REFERENCE.md для показа пользователю"""
        return self.EPERM_REF if self.EPERM_REF.exists() else None


# Глобальный экземпляр
_guard_instance: Optional[FileAccessGuard] = None


def get_guard() -> FileAccessGuard:
    """Возвращает (или создает) глобальный экземпляр FileAccessGuard"""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = FileAccessGuard()
    return _guard_instance


def before_write(file_path: str) -> Tuple[bool, str]:
    """
    Главная функция для проверки перед записью файла.

    Returns:
        (can_write, message)
    """
    return get_guard().before_write_operation(file_path)


def diagnose_eperm(file_path: str, original_error: str = "") -> Tuple[bool, str, str]:
    """
    Диагностирует EPERM и пытается исправить.

    Returns:
        (fixed, diagnosis, action)
    """
    return get_guard().diagnose_eperm(file_path, original_error)


def remove_readonly_dir(directory: str, pattern: str = "*") -> Tuple[int, List[str]]:
    """Снимает Read-Only со всех файлов в директории"""
    return get_guard().remove_readonly_recursive(directory, pattern)


# CLI для тестирования
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="File Access Guard V3 — Защита от EPERM")
    parser.add_argument('file', nargs='?', help='Путь к файлу')
    parser.add_argument('--before-write', action='store_true', help='Проверить перед записью')
    parser.add_argument('--diagnose', action='store_true', help='Диагностировать EPERM')
    parser.add_argument('--remove-readonly-dir', action='store_true', help='Снять Read-Only с директории')

    args = parser.parse_args()

    guard = get_guard()

    if args.before_write or (not args.diagnose and not args.remove_readonly_dir):
        if not args.file:
            print("Укажите путь к файлу")
            sys.exit(1)
        can_write, message = guard.before_write_operation(args.file)
        print(f"Can Write: {can_write}")
        print(f"Message: {message}")
        sys.exit(0 if can_write else 1)

    elif args.diagnose:
        if not args.file:
            print("Укажите путь к файлу")
            sys.exit(1)
        fixed, diagnosis, action = guard.diagnose_eperm(args.file)
        print(f"Fixed: {fixed}")
        print(f"Diagnosis: {diagnosis}")
        print(f"Action: {action}")
        sys.exit(0 if fixed else 1)

    elif args.remove_readonly_dir:
        directory = args.file or "C:/CLI/Pi/rules_imp"
        count, errors = guard.remove_readonly_recursive(directory)
        print(f"Files processed: {count}")
        if errors:
            print(f"Errors: {len(errors)}")
            for e in errors[:5]:
                print(f"  - {e}")
