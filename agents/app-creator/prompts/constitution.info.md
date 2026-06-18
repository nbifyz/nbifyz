---
name: constitution
description: Проверить соответствие конституции проекта
---

# /constitution

Прочитай `./rules/spec_principles.md`, раздел 4.
Создай `Prj/constitution.md` с принципами:
- Library-first — каждая фича как самостоятельная библиотека
- CLI Interface — текстовый протокол stdin/stdout, JSON + human-readable
- Test-First (NON-NEGOTIABLE) — TDD строго: Tests → Approve → Fail → Implement
- Integration Testing — контракты, межсервисная коммуникация, shared schemas

Проверь текущую реализацию на соответствие конституции.
Результат запиши в `Prj/constitution.md`:
- Соответствует / Не соответствует по каждому принципу
- Если не соответствует — что исправить
- Governance: поправки требуют документации + одобрения + плана миграции
