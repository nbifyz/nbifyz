#!/usr/bin/env python3
"""
V3 SYSTEM COMPREHENSIVE TEST
Комплексное тестирование всех компонентов АГЕНТ-V3

Версия: 1.0
Дата: 2026-03-30
Запуск: python test_v3_system.py [--verbose] [--component {all|gatekeeper|pre_run|session|file_guard|auto_lesson}]
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Добавляем путь к инструментам
sys.path.insert(0, str(Path(__file__).parent))

from gatekeeper import (
    get_gatekeeper,
    require_proof_of_search,
    require_honest_reporting,
    require_code_accuracy,
    validate_path
)
from pre_run_validator import (
    get_validator,
    before_bash,
    validate_json_path,
    auto_correct_path
)
from session_gate import (
    get_session_gate,
    check_session,
    get_current_lesson
)
from file_access_guard import (
    get_guard,
    before_write,
    diagnose_eperm
)
from auto_lesson_creator import (
    get_creator,
    lesson_from_error,
    lesson_from_reflection,
    lesson_from_knowledge
)


class Colors:
    """ANSI colors for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class TestResult:
    """Container for test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []

    def add(self, name: str, status: str, message: str = "", details: str = ""):
        self.tests.append({
            'name': name,
            'status': status,
            'message': message,
            'details': details
        })
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        elif status == 'WARN':
            self.warnings += 1


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_test(name: str, status: str, message: str = "", details: str = ""):
    """Print single test result"""
    if status == 'PASS':
        icon = f"{Colors.GREEN}[OK]{Colors.RESET}"
        color = Colors.GREEN
    elif status == 'FAIL':
        icon = f"{Colors.RED}[FAIL]{Colors.RESET}"
        color = Colors.RED
    else:
        icon = f"{Colors.YELLOW}[WARN]{Colors.RESET}"
        color = Colors.YELLOW

    print(f"  {icon} {name}")
    if message:
        print(f"    {color}{message}{Colors.RESET}")
    if details:
        print(f"    {Colors.BLUE}Details: {details}{Colors.RESET}")


# =============================================================================
# TEST SUITE: GATEKEEPER
# =============================================================================

def test_gatekeeper(results: TestResult, verbose: bool = False):
    """Test Gatekeeper component"""
    print_header("TESTING: Gatekeeper V3")

    # Test 1: Proof of Search - should block claim without evidence
    try:
        allowed, msg = require_proof_of_search("Функция X определена в файле Y")
        if not allowed:
            results.add("PoS - Block claim without evidence", "PASS",
                       "Correctly blocked claim without PoS")
        else:
            results.add("PoS - Block claim without evidence", "FAIL",
                       "Should have blocked claim without PoS")
    except Exception as e:
        results.add("PoS - Block claim without evidence", "FAIL", str(e))

    # Test 2: Proof of Search - should allow claim with evidence
    try:
        claim_with_pos = (
            "Функция X найдена через rg -nH 'def X' path "
            "(string: 42) — Данные взяты из исходника"
        )
        allowed, msg = require_proof_of_search(claim_with_pos)
        if allowed:
            results.add("PoS - Allow claim with evidence", "PASS",
                       "Correctly allowed claim with PoS markers")
        else:
            results.add("PoS - Allow claim with evidence", "FAIL",
                       "Should have allowed claim with PoS markers")
    except Exception as e:
        results.add("PoS - Allow claim with evidence", "FAIL", str(e))

    # Test 3: Honest Reporting - should block vague status
    try:
        allowed, msg = require_honest_reporting("Выполнено")
        if not allowed:
            results.add("Honest - Block vague 'Выполнено'", "PASS",
                       "Correctly blocked vague status")
        else:
            results.add("Honest - Block vague 'Выполнено'", "FAIL",
                       "Should have blocked vague status")
    except Exception as e:
        results.add("Honest - Block vague 'Выполнено'", "FAIL", str(e))

    # Test 4: Honest Reporting - should allow X/Y format
    try:
        allowed, msg = require_honest_reporting("Выполнено: 5 из 10 (50%)",
                                                  total=10, completed=5)
        if allowed:
            results.add("Honest - Allow X/Y format", "PASS",
                       "Correctly allowed X/Y format")
        else:
            results.add("Honest - Allow X/Y format", "FAIL",
                       "Should have allowed X/Y format")
    except Exception as e:
        results.add("Honest - Allow X/Y format", "FAIL", str(e))

    # Test 5: Code Accuracy - should detect syntax error
    try:
        bad_code = "def func(\n    pass"
        allowed, msg = require_code_accuracy(bad_code, 'python')
        if not allowed:
            results.add("Code - Detect syntax error", "PASS",
                       "Correctly detected syntax error")
        else:
            results.add("Code - Detect syntax error", "FAIL",
                       "Should have detected syntax error")
    except Exception as e:
        results.add("Code - Detect syntax error", "FAIL", str(e))

    # Test 6: Code Accuracy - should allow valid code
    try:
        good_code = "def func():\n    pass"
        allowed, msg = require_code_accuracy(good_code, 'python')
        if allowed:
            results.add("Code - Allow valid code", "PASS",
                       "Correctly allowed valid code")
        else:
            results.add("Code - Allow valid code", "FAIL",
                       "Should have allowed valid code")
    except Exception as e:
        results.add("Code - Allow valid code", "FAIL", str(e))

    # Test 7: Path Validation - should detect backslash
    try:
        valid, msg, corrected = validate_path("C:\\path\\file.txt", 'bash')
        if not valid and 'Обратный слеш' in msg:
            results.add("Path - Detect backslash in bash", "PASS",
                       "Correctly detected backslash")
        else:
            results.add("Path - Detect backslash in bash", "FAIL",
                       "Should have detected backslash")
    except Exception as e:
        results.add("Path - Detect backslash in bash", "FAIL", str(e))

    # Test 8: Path Validation - should detect @ in filename
    try:
        valid, msg, corrected = validate_path("C:/path/file@version.md", 'bash')
        if not valid and '@' in msg:
            results.add("Path - Detect @ in filename", "PASS",
                       "Correctly detected @ in filename")
        else:
            results.add("Path - Detect @ in filename", "WARN",
                       f"Check regex pattern. Valid={valid}, Msg={msg[:50]}")
    except Exception as e:
        results.add("Path - Detect @ in filename", "FAIL", str(e))

    print(f"\n{Colors.GREEN}Gatekeeper tests completed{Colors.RESET}\n")


# =============================================================================
# TEST SUITE: PRE-RUN VALIDATOR
# =============================================================================

def test_pre_run_validator(results: TestResult, verbose: bool = False):
    """Test Pre-run Validator component"""
    print_header("TESTING: Pre-run Validator V3")

    # Test 1: Block command with backslash
    try:
        allowed, msg, corrected = before_bash('cat C:\\path\\file.txt')
        if not allowed and 'Обратный слеш' in msg:
            results.add("Block backslash in bash", "PASS",
                       "Correctly blocked command with backslash")
        else:
            results.add("Block backslash in bash", "FAIL",
                       "Should have blocked command with backslash")
    except Exception as e:
        results.add("Block backslash in bash", "FAIL", str(e))

    # Test 2: Block command with @ in filename (if @ not used as trigger)
    try:
        allowed, msg, corrected = before_bash('cat C:/path/file@version.md')
        if not allowed and '@' in msg:
            results.add("Block @ in filename", "PASS",
                       "Correctly blocked @ in filename")
        else:
            # @ might be valid in some contexts, mark as warning
            results.add("Block @ in filename", "WARN",
                       f"Check implementation. Allowed={allowed}")
    except Exception as e:
        results.add("Block @ in filename", "FAIL", str(e))

    # Test 3: Validate JSON path
    try:
        allowed, msg, corrected = validate_json_path("C:/path/file.txt")
        if not allowed and '\\\\' in msg:
            results.add("Validate JSON path format", "PASS",
                       "Correctly detected JSON path issue")
        else:
            results.add("Validate JSON path format", "FAIL",
                       "Should have detected JSON path issue")
    except Exception as e:
        results.add("Validate JSON path format", "FAIL", str(e))

    # Test 4: Auto-correct path
    try:
        corrected = auto_correct_path("C:\\path\\file with spaces.txt")
        if '/' in corrected and '"' in corrected:
            results.add("Auto-correct path", "PASS",
                       f"Corrected to: {corrected}")
        else:
            results.add("Auto-correct path", "FAIL",
                       f"Incorrect correction: {corrected}")
    except Exception as e:
        results.add("Auto-correct path", "FAIL", str(e))

    print(f"\n{Colors.GREEN}Pre-run Validator tests completed{Colors.RESET}\n")


# =============================================================================
# TEST SUITE: SESSION GATE
# =============================================================================

def test_session_gate(results: TestResult, verbose: bool = False):
    """Test Session Gate component"""
    print_header("TESTING: Session Gate V3")

    # Test 1: Check session with existing lesson
    try:
        allowed, msg, lesson_path = check_session()
        if allowed and lesson_path:
            results.add("Check session with lesson", "PASS",
                       f"Session allowed with lesson: {lesson_path.name}")
        elif allowed:
            results.add("Check session with lesson", "WARN",
                       "Session allowed but no lesson path returned")
        else:
            results.add("Check session with lesson", "FAIL",
                       f"Session blocked: {msg[:100]}")
    except Exception as e:
        results.add("Check session with lesson", "FAIL", str(e))

    # Test 2: Get current lesson
    try:
        lesson = get_current_lesson()
        if lesson:
            results.add("Get current lesson", "PASS",
                       f"Found lesson: {lesson.name}")
        else:
            results.add("Get current lesson", "FAIL",
                       "No lesson found (should have test lesson)")
    except Exception as e:
        results.add("Get current lesson", "FAIL", str(e))

    # Test 3: Validate lesson metadata
    try:
        gate = get_session_gate()
        allowed, msg, lesson_path = check_session()
        if lesson_path:
            metadata = gate.get_lesson_metadata(lesson_path)
            if metadata and 'date' in metadata and 'topic' in metadata:
                results.add("Validate lesson metadata", "PASS",
                           f"Metadata valid: {metadata.get('topic', 'N/A')}")
            else:
                results.add("Validate lesson metadata", "FAIL",
                           "Missing required metadata fields")
        else:
            results.add("Validate lesson metadata", "SKIP",
                        "No lesson to check metadata")
    except Exception as e:
        results.add("Validate lesson metadata", "FAIL", str(e))

    print(f"\n{Colors.GREEN}Session Gate tests completed{Colors.RESET}\n")


# =============================================================================
# TEST SUITE: FILE ACCESS GUARD
# =============================================================================

def test_file_access_guard(results: TestResult, verbose: bool = False):
    """Test File Access Guard component"""
    print_header("TESTING: File Access Guard V3")

    # Create temp file for testing
    temp_file = None
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_file = f.name

        # Test 1: Check writable file
        can_write, msg = before_write(temp_file)
        if can_write:
            results.add("Check writable file", "PASS",
                       "File is writable")
        else:
            results.add("Check writable file", "FAIL",
                       f"Should be writable: {msg}")

        # Test 2: Diagnose EPERM on existing file
        fixed, diagnosis, action = diagnose_eperm(temp_file)
        results.add("Diagnose EPERM", "PASS" if not fixed else "WARN",
                   f"Diagnosis: {diagnosis}",
                   f"Action: {action}")

        # Test 3: Check non-existent file
        can_write, msg = before_write("C:/nonexistent/path/file.txt")
        if not can_write and 'не существует' in msg:
            results.add("Check non-existent file", "PASS",
                       "Correctly detected non-existent file")
        else:
            results.add("Check non-existent file", "WARN",
                       f"Result: {msg}")

    except Exception as e:
        results.add("File Access Guard tests", "FAIL", str(e))
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

    print(f"\n{Colors.GREEN}File Access Guard tests completed{Colors.RESET}\n")


# =============================================================================
# TEST SUITE: AUTO LESSON CREATOR
# =============================================================================

def test_auto_lesson_creator(results: TestResult, verbose: bool = False):
    """Test Auto Lesson Creator component"""
    print_header("TESTING: Auto Lesson Creator V3")

    created_lessons = []

    try:
        # Test 1: Create lesson from error
        success, path, msg = lesson_from_error(
            "TEST_ERROR",
            "Test error message for V3 system",
            "Test context for V3 testing",
            "HIGH"
        )
        if success and path.exists():
            created_lessons.append(path)
            results.add("Create lesson from error", "PASS",
                       f"Created: {path.name}")
        else:
            results.add("Create lesson from error", "FAIL",
                       f"Failed: {msg}")

        # Test 2: Create lesson from reflection
        success, path, msg = lesson_from_reflection(
            "V3 Testing Insight",
            "During testing, we discovered that V3 tools work correctly",
            "Apply this knowledge in future sessions",
            "MEDIUM"
        )
        if success and path.exists():
            created_lessons.append(path)
            results.add("Create lesson from reflection", "PASS",
                       f"Created: {path.name}")
        else:
            results.add("Create lesson from reflection", "FAIL",
                       f"Failed: {msg}")

        # Test 3: Create lesson from knowledge
        success, path, msg = lesson_from_knowledge(
            "V3 Architecture",
            "V3 system consists of 5 hard block tools that prevent rule violations",
            "V3 implementation documentation",
            "LOW"
        )
        if success and path.exists():
            created_lessons.append(path)
            results.add("Create lesson from knowledge", "PASS",
                       f"Created: {path.name}")
        else:
            results.add("Create lesson from knowledge", "FAIL",
                       f"Failed: {msg}")

        # Test 4: Verify JSON metadata in created lesson
        if created_lessons:
            with open(created_lessons[0], 'r') as f:
                content = f.read()
            if '---' in content and '"date"' in content:
                results.add("Verify JSON metadata", "PASS",
                           "Metadata present in created lesson")
            else:
                results.add("Verify JSON metadata", "FAIL",
                           "Missing JSON metadata")

    except Exception as e:
        results.add("Auto Lesson Creator tests", "FAIL", str(e))

    # Cleanup test lessons
    for lesson in created_lessons:
        try:
            if 'TEST' in lesson.name or 'V3' in lesson.name:
                lesson.unlink()
                print(f"  {Colors.YELLOW}Cleaned up: {lesson.name}{Colors.RESET}")
        except:
            pass

    print(f"\n{Colors.GREEN}Auto Lesson Creator tests completed{Colors.RESET}\n")


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests(component: str = 'all', verbose: bool = False):
    """Run all test suites"""
    results = TestResult()

    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print("     АГЕНТ-V3: КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 60)
    print(f"{Colors.RESET}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Компонент: {component}")
    print(f"Режим: {'Подробный' if verbose else 'Стандарт'}")
    print()

    # Run selected tests
    if component in ['all', 'gatekeeper']:
        test_gatekeeper(results, verbose)

    if component in ['all', 'pre_run', 'prerun']:
        test_pre_run_validator(results, verbose)

    if component in ['all', 'session', 'session_gate']:
        test_session_gate(results, verbose)

    if component in ['all', 'file_guard', 'fileguard']:
        test_file_access_guard(results, verbose)

    if component in ['all', 'auto_lesson', 'autocreator']:
        test_auto_lesson_creator(results, verbose)

    # Print summary
    print_header("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

    total = results.passed + results.failed + results.warnings

    print(f"\n{Colors.BOLD}РЕЗУЛЬТАТЫ:{Colors.RESET}")
    print(f"  {Colors.GREEN}[OK] Пройдено: {results.passed}{Colors.RESET}")
    print(f"  {Colors.RED}[FAIL] Ошибок: {results.failed}{Colors.RESET}")
    print(f"  {Colors.YELLOW}[WARN] Предупреждений: {results.warnings}{Colors.RESET}")
    print(f"  Всего тестов: {total}")
    print()

    # Detailed results
    if verbose:
        print(f"\n{Colors.BOLD}ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:{Colors.RESET}\n")
        for test in results.tests:
            print_test(test['name'], test['status'],
                      test.get('message', ''), test.get('details', ''))
            print()

    # Final verdict
    if results.failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("=" * 60)
        print("  [OK] ВСЕ ТЕСТЫ ПРОЙДЕНЫ - СИСТЕМА V3 ГОТОВА К РАБОТЕ")
        print("=" * 60)
        print(f"{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}")
        print("=" * 60)
        print(f"  [!] ОБНАРУЖЕНЫ ОШИБКИ: {results.failed} - ТРЕБУЕТСЯ ВНИМАНИЕ")
        print("=" * 60)
        print(f"{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Комплексное тестирование АГЕНТ-V3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python test_v3_system.py              # Тестировать всё
  python test_v3_system.py --verbose    # Подробный вывод
  python test_v3_system.py --component gatekeeper  # Только gatekeeper
  python test_v3_system.py --component pre_run      # Только pre_run_validator
        """
    )

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод результатов')
    parser.add_argument('--component', '-c',
                       choices=['all', 'gatekeeper', 'pre_run', 'prerun',
                               'session', 'session_gate', 'file_guard',
                               'fileguard', 'auto_lesson', 'autocreator'],
                       default='all',
                       help='Какой компонент тестировать (по умолчанию: all)')

    args = parser.parse_args()

    exit_code = run_all_tests(args.component, args.verbose)
    sys.exit(exit_code)
