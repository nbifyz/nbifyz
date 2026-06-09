# План и Лог Рефакторинга Директории Rules

Этот файл документирует процесс переноса и улучшения правил из `C:\CLI\piules` в `C:\CLI\piules_imp`.

## Этап 1: Создание структуры (Выполнено)

1.  Создана корневая папка: `C:\CLI\piules_imp`
2.  Созданы подпапки: `00_core`, `10_proc`, `20_skill`, `30_tool`, `90_skill_lib`.

## Этап 2: Миграция, Переименование и Объединение

- [ ] **Ядро (в `00_core`):**
    - [ ] `_global_Rules.md` → `id.md`
    - [ ] `_memory_strategy.md` → `memory.md`
    - [ ] `user_directives.md` → `directives.md`
- [ ] **Процессы (в `10_proc`):**
    - [ ] `_session_start_algorithm.md` → `p_start.md`
    - [ ] `main_control.md` → `p_loop.md`
    - [ ] `fix.md` → `p_fix.md`
    - [ ] `_services_monitoring.md` → `p_svcs.md`
- [ ] **Навыки (в `20_skill`):**
    - [ ] `search_mastery.md` → `s_search.md`
    - [ ] `02_code_analysis.md` → `s_analyze.md`
    - [ ] `04_error_handling.md` → `s_error.md`
    - [ ] `05_documentation.md` → `s_docs.md`
    - [ ] `06_validation.md` → `s_valid.md`
    - [ ] `07_dry_run.md` → `s_dryrun.md`
    - [ ] `08_iterative_development.md` → `s_iter.md`
    - [ ] **Объединить:** `tdd.md` + `03_testing_discipline.md` → `s_test.md`
    - [ ] **Объединить:** `use_rg.md` + `use_sd.md` → `s_tools.md`
- [ ] **Инструменты (в `30_tool`):**
    - [ ] Скопировать все файлы `.py` и `.bat`.
- [ ] **Библиотека навыков (в `90_skill_lib`):**
    - [ ] Скопировать все содержимое папки `rules/skills`.

## Этап 3: Создание индексных файлов

- [ ] Создать `_list_rules.md`.
- [ ] Создать `_list_tools.md`.

## Этап 4: Обновление AGENTS.md

- [ ] Обновить пути в `AGENTS.md` для соответствия новой структуре.
