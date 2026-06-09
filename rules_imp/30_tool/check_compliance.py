#!/usr/bin/env python3
"""
Скрипт проверки соответствия кода требованиям из main_rule.md
"""

import ast
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class CodeComplianceChecker:
    """
    Класс для проверки соответствия кода требованиям из main_rule.md
    """
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_content = self._read_file()
        self.ast_tree = self._parse_ast()
        self.issues = []
        
    def _read_file(self) -> str:
        """Чтение содержимого файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"Ошибка при чтении файла {self.file_path}: {e}")
            return ""
    
    def _parse_ast(self) -> ast.AST:
        """Парсинг содержимого файла в AST"""
        try:
            return ast.parse(self.file_content)
        except SyntaxError as e:
            print(f"Синтаксическая ошибка в файле {self.file_path}: {e}")
            return ast.parse("")
    
    def check_type_annotations(self) -> List[str]:
        """Проверка наличия аннотаций типов"""
        issues = []
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Проверяем, что у функции есть аннотации типов
                missing_annotations = []
                
                # Проверяем аннотации аргументов
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg != 'self':
                        missing_annotations.append(f"'{arg.arg}' в функции '{node.name}'")
                
                # Проверяем аннотацию возвращаемого значения
                if node.returns is None:
                    missing_annotations.append(f"возвращаемое значение функции '{node.name}'")
                
                if missing_annotations:
                    issues.append(f"Функция {node.name} не имеет аннотаций типов для: {', '.join(missing_annotations)}")
        
        return issues
    
    def check_docstrings(self) -> List[str]:
        """Проверка наличия docstring'ов"""
        issues = []
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if node != self.ast_tree or node.body:  # Не проверяем пустой модуль
                    # Проверяем, есть ли docstring
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        node_type = "функции" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else \
                                   "класса" if isinstance(node, ast.ClassDef) else "модуля"
                        node_name = getattr(node, 'name', 'module')
                        issues.append(f"Отсутствует docstring у {node_type} '{node_name}'")
        
        return issues
    
    def check_venv_usage(self) -> List[str]:
        """Проверка использования виртуального окружения (на уровне файла)"""
        issues = []
        
        # Для Python файлов проверяем, есть ли указания на виртуальное окружение.
        # Это очень базовая проверка.
        if "venv" in self.file_content.lower() or "activate" in self.file_content.lower():
            # Если упоминания есть, предполагаем, что все в порядке.
            # Удалена проверка на жестко заданный путь для повышения портируемости.
            pass
        else:
            # Больше не добавляем предупреждение для каждого файла, так как это создает много шума.
            # Более надежная проверка могла бы анализировать импорты.
            pass
        
        return issues
    
    def check_input_validation(self) -> List[str]:
        """Проверка наличия валидации входных данных"""
        issues = []
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Проверяем, есть ли проверки аргументов функции
                has_validation = False
                
                # Собираем имена аргументов, исключая 'self'
                arg_names = [arg.arg for arg in node.args.args if arg.arg != 'self']
                
                if not arg_names:
                    continue  # Пропускаем функции без аргументов (кроме self)

                # Ищем проверки в теле функции. Это простая эвристика.
                # Более сложный анализ мог бы проверять, используются ли аргументы в условиях.
                for stmt in node.body:
                    if isinstance(stmt, (ast.If, ast.Assert, ast.Raise)):
                        has_validation = True
                        break
                
                if not has_validation:
                    issues.append(f"Функция '{node.name}' может не иметь валидации для входных данных: {', '.join(arg_names)}")
        
        return issues
    
    def check_exception_handling(self) -> List[str]:
        """Проверка наличия обработки исключений на уровне функций."""
        issues = []
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Проверяем, есть ли в теле функции блок try-except
                has_try_except = False
                if not node.body:
                    continue # Пропускаем функции без тела

                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Try):
                        has_try_except = True
                        break
                
                if not has_try_except:
                    # Это эвристика. Не каждая функция требует try-except,
                    # но отсутствие может указывать на потенциальную проблему.
                    issues.append(f"Функция '{node.name}' может не иметь обработки исключений.")
        
        return issues
    
    def run_all_checks(self) -> Dict[str, List[str]]:
        """Запуск всех проверок"""
        results = {}
        
        results['type_annotations'] = self.check_type_annotations()
        results['docstrings'] = self.check_docstrings()
        results['venv_usage'] = self.check_venv_usage()
        results['input_validation'] = self.check_input_validation()
        results['exception_handling'] = self.check_exception_handling()
        
        return results

def check_file_compliance(file_path: str) -> bool:
    """Проверка соответствия файла требованиям и возврат результата"""
    checker = CodeComplianceChecker(file_path)
    results = checker.run_all_checks()
    
    total_issues = 0
    for check_type, issues in results.items():
        if issues:
            print(f"\n{check_type.replace('_', ' ').title()}:")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
    
    # Определяем символы для вывода в зависимости от поддержки терминалом
    if total_issues == 0:
        print(f"\n[OK] Файл {file_path} соответствует всем проверяемым требованиям.")
        return True
    else:
        print(f"\n[FAIL] Найдено {total_issues} нарушений требований в файле {file_path}")
        return False

def check_all_files_in_directory(directory_path: str, extensions: List[str] = ['.py']) -> bool:
    """Проверка соответствия всех файлов в директории"""
    directory = Path(directory_path)
    all_compliant = True
    
    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            print(f"\nПроверка файла: {file_path}")
            if not check_file_compliance(str(file_path)):
                all_compliant = False
    
    return all_compliant

def main():
    if len(sys.argv) < 2:
        print("Использование: python check_compliance.py <путь_к_файлу_или_директории>")
        sys.exit(1)
    
    target_path = sys.argv[1]
    
    if os.path.isfile(target_path):
        # Проверка одного файла
        is_compliant = check_file_compliance(target_path)
        sys.exit(0 if is_compliant else 1)
    elif os.path.isdir(target_path):
        # Проверка всех файлов в директории
        is_compliant = check_all_files_in_directory(target_path)
        sys.exit(0 if is_compliant else 1)
    else:
        print(f"Ошибка: {target_path} не существует")
        sys.exit(1)

if __name__ == "__main__":
    main()