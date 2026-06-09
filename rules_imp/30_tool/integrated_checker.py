#!/usr/bin/env python3
"""
Интеграционная система проверки соответствия кода требованиям main_rule.md
Объединяет все разработанные компоненты в единую систему
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

# Определяем путь к директории, где находится integrated_checker.py
RULES_DIR = Path(__file__).parent

def run_compliance_check(file_path: str) -> (bool, str, str): # Return success, stdout, and error message
    """Запуск проверки соответствия кода требованиям"""
    compliance_script_path = RULES_DIR / "check_compliance.py"
    cmd = [sys.executable, str(compliance_script_path), file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.returncode == 0, result.stdout, result.stderr

def run_dry_run_analysis(file_path: str) -> (bool, str, str): # Return success, stdout, and error message
    """Запуск сухого прогона кода"""
    dry_run_script_path = RULES_DIR / "dry_run_analyzer.py"
    cmd = [sys.executable, str(dry_run_script_path), file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.returncode == 0, result.stdout, result.stderr

VENV_PATH = Path("C:\\Projects\\venv") # Системный venv согласно Протоколу_3 и новой инструкции пользователя

def activate_venv_and_run_script(file_path: str) -> (bool, str, str): # Changed script_path to file_path
    """Активация venv и запуск скрипта/попытка импорта модуля с использованием исполняемого файла Python из venv."""
    
    file_path_obj = Path(file_path) # Convert to Path object once
    
    if not file_path_obj.exists():
        return False, "", f"ОШИБКА: Файл {file_path} не существует"

    if sys.platform == "win32":
        python_executable = VENV_PATH / "Scripts" / "python.exe"
    else:
        python_executable = VENV_PATH / "bin" / "python"

    if not python_executable.exists():
        return False, "", f"ОШИБКА: Исполняемый файл Python не найден в venv: {python_executable}"
    
    # Определяем, является ли файл частью пакета 'app/'
    if "app" in file_path_obj.parts and file_path_obj.suffix == ".py":
        # Для модулей внутри 'app/', пытаемся импортировать
        # Преобразуем путь к файлу в имя модуля (например, app/my_module.py -> app.my_module)
        module_name = ".".join(file_path_obj.parts[:-1] + (file_path_obj.stem,))
        # Используем -c для выполнения Python кода, который пытается импортировать модуль
        cmd = [
            str(python_executable),
            "-c",
            f"import sys; sys.path.append('.'); import {module_name}" # Добавляем текущую директорию в PYTHONPATH
        ]
        # Пропускаем вывод print() функций из if __name__ == "__main__"
        # Для этого нужно изменить способ запуска, чтобы он не выполнял блок __main__
        # Самый простой способ: запускать pytest или использовать ast.parse
        # Но цель integrated_checker - проверить именно "выполнение"
        # Поэтому мы будем импортировать и игнорировать stderr (пока)
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Обрабатываем stderr отдельно, так как print() из __main__ попадет в stdout
        if result.returncode != 0:
            return False, result.stdout, f"ОШИБКИ ИМПОРТА МОДУЛЯ: {result.stderr}"
        else:
            return True, result.stdout, result.stderr

    else:
        # Для других скриптов, запускаем их напрямую
        cmd = [str(python_executable), file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0, result.stdout, result.stderr

def comprehensive_check(file_path: str) -> bool:
    """Комплексная проверка файла"""
    print(f"Начинаем комплексную проверку файла: {file_path}")
    print("="*60)
    
    all_checks_passed = True
    all_errors = []
    
    # 1. Проверка соответствия требованиям
    print("\n=== Запуск проверки соответствия кода требованиям ===")
    compliance_passed, compliance_stdout, compliance_stderr = run_compliance_check(file_path)
    print(compliance_stdout)
    if not compliance_passed:
        print("❌ Проверка соответствия требованиям НЕ ПРОЙДЕНА")
        all_checks_passed = False
        if compliance_stderr:
            all_errors.append(f"ОШИБКИ СООТВЕТСТВИЯ: {compliance_stderr}")
    else:
        print("✅ Проверка соответствия требованиям пройдена")
    
    # 2. Сухой прогон
    print("\n=== Запуск сухого прогона кода ===")
    dry_run_passed, dry_run_stdout, dry_run_stderr = run_dry_run_analysis(file_path)
    print(dry_run_stdout)
    if not dry_run_passed:
        print("❌ Сухой прогон НЕ ПРОЙДЕН")
        all_checks_passed = False
        if dry_run_stderr:
            all_errors.append(f"ОШИБКИ СУХОГО ПРОГОНА: {dry_run_stderr}")
    else:
        print("✅ Сухой прогон пройден")
    
    # 3. Если это Python-файл, проверим его выполнение в venv
    if file_path.endswith('.py'):
        print(f"\n=== Запуск скрипта {file_path} в виртуальном окружении ===")
        execution_passed, execution_stdout, execution_stderr = activate_venv_and_run_script(file_path)
        print(execution_stdout)
        if not execution_passed:
            print("❌ Выполнение в venv НЕ ПРОЙДЕНО")
            all_checks_passed = False
            if execution_stderr:
                all_errors.append(f"ОШИБКИ ВЫПОЛНЕНИЯ VENV: {execution_stderr}")
        else:
            print("✅ Выполнение в venv пройдено")
    
    print("="*60)
    if all_errors:
        print("\n--- СВОДКА ОШИБОК ---")
        for error in all_errors:
            print(f"- {error}")
        print("---------------------")

    if all_checks_passed:
        print("🎉 Все проверки пройдены успешно!")
        return True
    else:
        print("❌ Не все проверки пройдены")
        return False

def main():
    parser = argparse.ArgumentParser(description='Интеграционная система проверки соответствия main_rule.md')
    parser.add_argument('path', help='Путь к файлу или директории для проверки')
    parser.add_argument('--all', action='store_true', help='Проверить все файлы в директории')
    
    args = parser.parse_args()
    
    target_path = Path(args.path)
    
    if not target_path.exists():
        print(f"Ошибка: {args.path} не существует")
        sys.exit(1)
    
    if target_path.is_file():
        # Проверяем один файл
        success = comprehensive_check(str(target_path))
        sys.exit(0 if success else 1)
    
    elif target_path.is_dir():
        # Проверяем все подходящие файлы в директории
        all_passed = True
        
        # Находим все Python файлы в директории
        py_files = list(target_path.rglob("*.py")) if args.all else [f for f in target_path.iterdir() if f.suffix == '.py']
        
        print(f"Найдено {len(py_files)} Python файлов для проверки")
        
        for py_file in py_files:
            print(f"\nПроверка файла: {py_file}")
            if not comprehensive_check(str(py_file)):
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 Все {len(py_files)} файлов прошли проверку!")
        else:
            print(f"\n❌ Не все из {len(py_files)} файлов прошли проверку")
        
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()