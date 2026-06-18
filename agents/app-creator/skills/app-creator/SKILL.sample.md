
---
name: app-creator
description: Автономный конвейер создания приложения от принципов до кода по SpecKit
---

# /app-creator

## Роли

| Агент | Модель | Задача |
|-------|--------|--------|
| `oracle` | Gemma (reasoning on) | Constitution, Analyze — принципы и кросс-анализ |
| `context-builder` | Qwen | Specify — спецификация |
| `scout` | Qwen | Clarify — аудит рисков и дефектов логики |
| `planner` | Qwen | Plan — план архитектуры |
| `reviewer` | Gemma (reasoning on) | Checklist — верификация требований |
| `worker` | Qwen | Tasks, Implement — задачи и код |

## Когда использовать

- Создание нового приложения с нуля
- Нужна полная цепочка SpecKit: принципы → спецификация → аудит → план → чеклист → задачи → анализ → код
- Требуется автономная работа без вопросов пользователю

## Пайплайн

### Шаг 0: Подготовка

1. Прочитай `./task.md` — получи задание.
2. Прочитай `./TS.md` — получи техническое задание.
3. Если неопределённость > 0.1 — задай вопросы пользователю (максимум 5).
4. Определи `PROJECT_ROOT` из `./PROJECT_NAME.md`.

---

### Шаг 1: Constitution (oracle, Gemma)

Переключи модель на Gemma: `/switch-model`

```
subagent({
  agent: "oracle",
  task: "Прочитай ./task.md и ./TS.md.
         Создай ./constitution.md с верхнеуровневыми принципами системы:
         - Library-first
         - CLI Interface
         - Test-First (NON-NEGOTIABLE)
         - Integration Testing
         Governance: поправки требуют документации + одобрения + плана миграции.
         
         Хук before: прочитай ./constitution.md если существует.
         Хук after: запиши ./constitution.md.",
  context: "fresh"
})
```

**Артефакт:** `./constitution.md`

**Маркер готовности:** `[CONSTITUTION_READY]`

---

### Шаг 2: Specify (context-builder, Qwen)

Переключи модель на Qwen: `/switch-model`

```
subagent({
  agent: "context-builder",
  task: "Прочитай ./constitution.md, ./task.md, ./TS.md.
         Создай ./spec.md по шаблону spec_principles.md (раздел 1):
         - User Scenarios & Testing (P1, P2, P3)
         - Requirements (FR-001, FR-002...)
         - Key Entities
         - Success Criteria
         - Edge Cases
         Неясное помечай [NEEDS CLARIFICATION].
         Противоречия разрешай автономно:
         - Приоритет 1: ТЗ пользователя
         - Приоритет 2: KISS (самое простое решение)
         - Приоритет 3: Оптимальное инженерное решение
         Фиксируй решения: [AUTONOMOUS_RESOLUTION]: ...
         
         Хук before: прочитай ./spec.md если существует.
         Хук after: запиши ./spec.md.",
  context: "fresh"
})
```

**Артефакт:** `./spec.md`

**Маркер готовности:** `[SPECIFY_READY]`

---

### Шаг 3: Clarify (scout, Qwen)

```
subagent({
  agent: "scout",
  task: "Прочитай ./spec.md, ./constitution.md, ./TS.md.
         Проведи ОБЯЗАТЕЛЬНЫЙ внутренний аудит:
         - Риски архитектуры
         - Скрытые дефекты логики
         - Противоречия между требованиями
         - Неоднозначности в спецификации
         
         Если есть [NEEDS CLARIFICATION] — разреши автономно по KISS.
         Обнови ./spec.md: добавь секцию ## Clarifications.
         Запиши все [AUTONOMOUS_RESOLUTION] в spec.md.
         
         Хук before: прочитай ./spec.md.
         Хук after: запиши обновлённый ./spec.md.",
  context: "fresh"
})
```

**Артефакт:** `./spec.md` (обновлённый)

**Маркер готовности:** `[CLARIFY_READY]`

---

### Шаг 4: Plan (planner, Qwen)

```
subagent({
  agent: "planner",
  task: "Прочитай ./spec.md, ./constitution.md.
         Создай ./plan.md:
         - Фазы: Setup → Foundational → User Stories (P1→P3) → Polish
         - Для каждой фазы: задачи с ID, приоритетом, зависимостями
         - Параллельные задачи помечай [P]
         - Архитектурные решения
         - Стек технологий (если указан в TS.md)
         
         Хук before: прочитай ./plan.md если существует.
         Хук after: запиши ./plan.md.",
  context: "fresh"
})
```

**Артефакт:** `./plan.md`

**Маркер готовности:** `[PLAN_READY]`

---

### Шаг 5: Checklist (reviewer, Gemma)

Переключи модель на Gemma: `/switch-model`

```
subagent({
  agent: "reviewer",
  task: "Прочитай ./spec.md, ./plan.md, ./constitution.md.
         Создай ./checklists/requirements.md по шаблону spec_principles.md (раздел 2):
         - CHK001, CHK002... для каждого требования из spec.md
         - Проверка покрытия тестами
         - Проверка соответствия конституции
         - Edge cases
         
         Хук before: прочитай ./checklists/requirements.md если существует.
         Хук after: запиши ./checklists/requirements.md.",
  context: "fresh"
})
```

**Артефакт:** `./checklists/requirements.md`

**Маркер готовности:** `[CHECKLIST_READY]`

---

### Шаг 6: Tasks (worker, Qwen)

Переключи модель на Qwen: `/switch-model`

```
subagent({
  agent: "worker",
  task: "Прочитай ./plan.md, ./spec.md, ./checklists/requirements.md.
         Создай ./tasks.md по шаблону spec_principles.md (раздел 3):
         - Фазы как в plan.md
         - Задачи: [ID] [P?] [Story] Описание
         - Точные пути к файлам
         - Зависимости между задачами
         - Стратегия: MVP First → Incremental Delivery
         
         Хук before: прочитай ./tasks.md если существует.
         Хук after: запиши ./tasks.md.",
  context: "fresh"
})
```

**Артефакт:** `./tasks.md`

**Маркер готовности:** `[TASKS_READY]`

---

### Шаг 7: Analyze (oracle, Gemma)

Переключи модель на Gemma: `/switch-model`

```
subagent({
  agent: "oracle",
  task: "Прочитай ВСЕ созданные документы:
         ./constitution.md, ./spec.md, ./plan.md, ./checklists/requirements.md, ./tasks.md.
         Проведи финальный кросс-анализ консистентности:
         - Нет ли противоречий между spec и plan
         - Все ли требования покрыты задачами
         - Соответствует ли план конституции
         - Все ли чеклисты покрывают требования
         Результат запиши в ./analysis.md:
         - Статус: CONSISTENT или INCONSISTENT
         - Если INCONSISTENT — список конфликтов
         - Рекомендации по исправлению
         
         Хук before: прочитай ./analysis.md если существует.
         Хук after: запиши ./analysis.md.",
  context: "fresh"
})
```

**Артефакт:** `./analysis.md`

**Маркер готовности:** `[ANALYZE_READY]`

---

### Шаг 8: Implement (worker, Qwen)

Переключи модель на Qwen: `/switch-model`

**ТОЛЬКО ЕСЛИ** `./analysis.md` = CONSISTENT.

```
subagent({
  agent: "worker",
  task: "Прочитай ./tasks.md, ./plan.md, ./spec.md.
         Выполняй задачи последовательно по фазам:
         1. Setup
         2. Foundational
         3. User Stories (P1 → P2 → P3)
         4. Polish
         
         Для каждой задачи:
         - Прочитай целевые файлы
         - Напиши код
         - Запиши файлы
         - Обнови project_structure.md: tree /f /a > project_structure.md
         - Отметь задачу [x] в ./tasks.md
         
         После каждой фазы — отчёт в ./session_history.md на русском.
         
         Хук before: прочитай ./tasks.md.
         Хук after: запиши обновлённый ./tasks.md и изменённые файлы.",
  context: "fresh"
})
```

**Артефакт:** Готовый код приложения

**Маркер готовности:** `[IMPLEMENT_READY]`

---

### Шаг 9: Завершение

1. Обнови `CURRENT_TASK.md` (`[x]`)
2. Запиши финальный отчёт в `./session_history.md`
3. Выполни `/compact` — сжать контекст, сохранив артефакты

---

## Хуки

Каждый шаг поддерживает хуки (из `./speckit/./extensions.yml`):

- **before_hook** (optional: false) — выполнить ДО шага. Если команда — EXECUTE_COMMAND.
- **after_hook** (optional: true) — выполнить ПОСЛЕ шага. Спросить пользователя.

## Ограничения

- Один шаг = одно сообщение = один subagent
- Переход к следующему шагу только после маркера готовности
- Автономное разрешение неоднозначностей (без вопросов пользователю)
- Максимум 5 вопросов пользователю только если неопределённость > 0.1 (Шаг 0)
- Только суб-агенты Pi
- Модели переключаются автоматически через `/switch-model`
