#!/usr/bin/env python3
"""
Система сухого прогона кода - анализ логики программного кода без его выполнения
"""

import ast
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

class DryRunAnalyzer:
    """
    Класс для анализа кода без его выполнения (сухой прогон)
    """
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_content = self._read_file()
        self.ast_tree = self._parse_ast()
        self.analysis_results = {
            'functions': [],
            'control_flow': [],
            'potential_issues': [],
            'dependencies': [],
            'data_flow': []
        }
        self.analysis_results = self.run_analysis() # Run analysis and store results
    
    def _read_file(self) -> str:
        """Чтение содержимого файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"Ошибка при чтении файла {self.file_path}: {e}")
            return ""
    
    def _parse_ast(self) -> Optional[ast.AST]:
        """Парсинг содержимого файла в AST"""
        try:
            return ast.parse(self.file_content)
        except SyntaxError as e:
            print(f"Синтаксическая ошибка в файле {self.file_path}: {e}")
            return None
    
    def analyze_functions(self) -> List[Dict[str, Any]]:
        """Анализ функций в коде"""
        functions = []
        
        if not self.ast_tree:
            return functions
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = {
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args if arg.arg != 'self'],
                    'returns': node.returns is not None,
                    'docstring': ast.get_docstring(node),
                    'body_lines': len(node.body),
                    'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node)),
                    'has_yield': any(isinstance(n, ast.Yield) for n in ast.walk(node)),
                    'complexity': self._calculate_complexity(node)
                }
                functions.append(func_info)
        
        return functions
    
    def _calculate_complexity(self, func_node) -> int:
        """Расчет цикломатической сложности функции"""
        complexity = 1  # базовая сложность
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.And, ast.Or)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def analyze_control_flow(self) -> List[Dict[str, Any]]:
        """Анализ управляющих конструкций"""
        control_flow = []
        
        if not self.ast_tree:
            return control_flow
            
        for node in ast.walk(self.ast_tree):
            control_info = None
            
            if isinstance(node, ast.If):
                control_info = {
                    'type': 'if',
                    'line': node.lineno,
                    'condition': ast.unparse(node.test) if hasattr(ast, 'unparse') else 'unknown'
                }
            elif isinstance(node, ast.For):
                control_info = {
                    'type': 'for',
                    'line': node.lineno,
                    'target': ast.unparse(node.target) if hasattr(ast, 'unparse') else 'unknown',
                    'iter': ast.unparse(node.iter) if hasattr(ast, 'unparse') else 'unknown'
                }
            elif isinstance(node, ast.While):
                control_info = {
                    'type': 'while',
                    'line': node.lineno,
                    'condition': ast.unparse(node.test) if hasattr(ast, 'unparse') else 'unknown'
                }
            elif isinstance(node, ast.Try):
                control_info = {
                    'type': 'try',
                    'line': node.lineno,
                    'handlers': len(node.handlers)
                }
            
            if control_info:
                control_flow.append(control_info)
        
        return control_flow
    
    def analyze_potential_issues(self) -> List[Dict[str, str]]:
        """Анализ потенциальных проблем в коде"""
        issues = []
        
        if not self.ast_tree:
            return issues
            
        for node in ast.walk(self.ast_tree):
            # Проверка на использование eval/exec (потенциально небезопасно)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'compile']:
                    issues.append({
                        'type': 'security_risk',
                        'line': node.lineno,
                        'message': f'Использование потенциально небезопасной функции {node.func.id}'
                    })
            
            # Проверка на деление на ноль
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    issues.append({
                        'type': 'division_by_zero',
                        'line': node.lineno,
                        'message': 'Потенциальное деление на ноль'
                    })
            
            # Проверка на пустые блоки
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)):
                if not node.body:
                    issues.append({
                        'type': 'empty_block',
                        'line': node.lineno,
                        'message': f'Пустой блок {type(node).__name__}'
                    })
        
        return issues
    
    def analyze_dependencies(self) -> List[str]:
        """Анализ импортов и зависимостей"""
        dependencies = []
        
        if not self.ast_tree:
            return dependencies
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    dependencies.append(f"{module}.{alias.name}")
        
        return list(set(dependencies))  # Уникальные зависимости
    
    def analyze_data_flow(self) -> List[Dict[str, Any]]:
        """Анализ потоков данных"""
        data_flow = []
        
        if not self.ast_tree:
            return data_flow
            
        # Словарь для отслеживания переменных
        variables = {}
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        variables[var_name] = {
                            'line': node.lineno,
                            'operation': 'assignment',
                            'value_type': type(node.value).__name__
                        }
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    variables[var_name] = {
                        'line': node.lineno,
                        'operation': 'annotation_assignment',
                        'value_type': type(node.value).__name__ if node.value else 'annotation_only'
                    }
        
        for var_name, info in variables.items():
            data_flow.append({
                'variable': var_name,
                'line': info['line'],
                'operation': info['operation'],
                'value_type': info['value_type']
            })
        
        return data_flow
    
    def run_analysis(self) -> Dict[str, Any]:
        """Запуск полного анализа"""
        if not self.ast_tree:
            return self.analysis_results
        
        self.analysis_results['functions'] = self.analyze_functions()
        self.analysis_results['control_flow'] = self.analyze_control_flow()
        self.analysis_results['potential_issues'] = self.analyze_potential_issues()
        self.analysis_results['dependencies'] = self.analyze_dependencies()
        self.analysis_results['data_flow'] = self.analyze_data_flow()
        
        return self.analysis_results
    
    def generate_report(self) -> str:
        """Генерация текстового отчета о сухом прогоне"""
        report = []
        report.append(f"=== Сухой прогон кода: {self.file_path} ===\n")
        
        analysis = self.analysis_results # Use stored analysis results
        
        # Функции
        report.append("ФУНКЦИИ:")
        for func in analysis['functions']:
            report.append(f"  - {func['name']} (линия {func['line']}) - аргументы: {func['args']}, сложность: {func['complexity']}")
            if func['docstring']:
                report.append(f"    Описание: {func['docstring'][:60]}...")
        
        # Управляющие конструкции
        report.append("\nУПРАВЛЯЮЩИЕ КОНСТРУКЦИИ:")
        for ctrl in analysis['control_flow']:
            report.append(f"  - {ctrl['type']} на линии {ctrl['line']}")
        
        # Потенциальные проблемы
        report.append("\nПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ:")
        if analysis['potential_issues']:
            for issue in analysis['potential_issues']:
                report.append(f"  - {issue['message']} на линии {issue['line']}")
        else:
            report.append("  - Проблемы не обнаружены")
        
        # Зависимости
        report.append(f"\nЗАВИСИМОСТИ ({len(analysis['dependencies'])}):")
        for dep in analysis['dependencies'][:10]:  # Показать первые 10
            report.append(f"  - {dep}")
        if len(analysis['dependencies']) > 10:
            report.append(f"  ... и еще {len(analysis['dependencies']) - 10}")
        
        # Потоки данных
        report.append(f"\nПЕРЕМЕННЫЕ ({len(analysis['data_flow'])}):")
        for var in analysis['data_flow'][:10]:  # Показать первые 10
            report.append(f"  - {var['variable']} ({var['value_type']}) на линии {var['line']}")
        if len(analysis['data_flow']) > 10:
            report.append(f"  ... и еще {len(analysis['data_flow']) - 10}")
        
        report.append(f"\n=== Анализ завершен ===")
        return "\n".join(report)

def main():
    if len(sys.argv) < 2:
        print("Использование: python dry_run_analyzer.py <путь_к_файлу>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Файл {file_path} не существует")
        sys.exit(1)
    
    analyzer = DryRunAnalyzer(file_path)
    report = analyzer.generate_report()
    print(report)

    # Определяем символы для вывода в зависимости от поддержки терминалом
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        CHECK = '[OK]'  # Заменяем на ASCII
        CROSS = '[FAIL]'  # Заменяем на ASCII
    else:
        CHECK = '[OK]'
        CROSS = '[FAIL]'

    if "Проблемы не обнаружены" in report: # Простая эвристика для определения успеха
        print(f"\n{CHECK} Сухой прогон завершен успешно. Проблемы не обнаружены.")
        sys.exit(0)
    else:
        print(f"\n{CROSS} Сухой прогон завершен с проблемами. Требуется анализ.")
        sys.exit(1)

if __name__ == "__main__":
    main()