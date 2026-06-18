# SKILL: app-creator-orchestration

## When to Use
Use this skill when you need to initialize, refine, or implement a structured project specification and codebase using the `app-creator` agent suite. It is ideal for transforming raw requirements or existing code into a formal set of artifacts (`spec.md`, `plan.md`, `tasks.md`).

## Procedure

### 1. Scouting Phase
- **Action**: Run the `scout` agent.
- **Goal**: Perform non-destructive exploration of the codebase/requirements.
- **Output**: A comprehensive `context.md` file detailing structure, dependencies, and potential issues.

### 2. Context & Planning Phase
- **Action**: Use `context-builder` and `planner` agents.
- **Goal**: Refine the scouted context into a formal project plan.
- **Output**: A structured `plan.md` that outlines architecture, stack choices, and implementation phases.

### 3. Implementation (Worker) Phase
- **Action**: Deploy `worker` agents (e.g., `implement`, `specify`, `tasks`).
- **Goal**: Execute the plan by generating/updating core artifacts:
    - `spec.md` (Requirements & Success Criteria)
    - `plan.md` (Architecture & Phases)
    - `tasks.md` (Atomic, actionable tasks)
- **Constraint**: Ensure all implementation steps respect the project's `constitution.md`.

### 4. Review Phase
- **Action**: Use the `reviewer` agent.
- **Goal**: Verify consistency between `spec.md`, `plan.md`, and `tasks.md`. Check for:
    - Duplications or ambiguities.
    - Underspecification.
    - Constitution violations (CRITICAL).
- **Loop**: If critical errors are found, return to the Worker phase (max 2 iterations).

### 5. Finalization (Oracle) Phase
- **Action**: Use the `oracle` agent.
- **Goal**: Provide a final verdict on the readiness of the specification and codebase for full-scale development.

## Pitfalls
- **Ignoring Constitution**: Failing to validate implementation against `constitution.md` can lead to critical architectural drift.
- **Skipping Review**: Moving straight to implementation without a formal review phase often results in inconsistent artifacts.
- **Incomplete Scouting**: Relying on shallow context leads to flawed plans and broken implementations.

## Verification Steps
- [ ] `spec.md`, `plan.md`, and `tasks.md` exist and are internally consistent.
- [ ] Every task in `tasks.md` is mapped to a requirement in `spec.md`.
- [ ] The implementation adheres to all principles defined in `constitution.md`.
- [ ] All extension hooks (if any) have been executed/checked.
