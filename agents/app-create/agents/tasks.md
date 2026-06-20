---

description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs: 
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before tasks generation)**:
- Check if `app-create/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_tasks` key.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
- If no hooks are registered or `app-create/extensions.yml` does not exist, skip silently.

## Outline

1. **Setup**: Run `check-prerequisites` skill (based on `.specify/scripts/powershell/check-prerequisites.ps1`) from repo root and parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute.

2. **Load design documents**: Read from `app-create/specs/<branch_name>/`:
   - **Required**: `plan.md` (tech stack, libraries, structure), `spec.md` (user stories with priorities)
   - **Optional**: `data-model.md` (entities), `contracts/` (interface contracts), `research.md` (decisions), `quickstart.md` (test scenarios)

3. **Execute task generation workflow**:
   - Load `plan.md` and extract tech stack, libraries, project structure.
   - Load `spec.md` and extract user stories with their priorities (P1, P2, P3, etc.).
   - If `data-model.md` exists: Extract entities and map to user stories.
   - If `contracts/` exists: Map interface contracts to user stories.
   - If `research.md` exists: Extract decisions for setup tasks.
   - Generate tasks organized by user story (see Task Generation Rules below).
   - Generate dependency graph showing user story completion order.
   - Create parallel execution examples per user story.
   - Validate task completeness (each user story has all needed tasks, independently testable).

4. **Generate `tasks.md`**: Use `app-create/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from `plan.md`.
   - Phase 1: Setup tasks (project initialization).
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories).
   - Phase 3+: One phase per user story (in priority order from `spec.md`).
   - Final Phase: Polish & cross-cutting concerns.
   - All tasks must follow the strict checklist format (see Task Generation Rules below).
   - Clear file paths for each task.
   - Dependencies section showing story completion order.
   - Parallel execution examples per story.
   - Implementation strategy section (MVP first, incremental delivery).

5. **Report**: Output path to generated `tasks.md` and summary:
   - Total task count.
   - Task count per user story.
   - Parallel opportunities identified.
   - Independent test criteria for each story.
   - Suggested MVP scope (typically just User Story 1).
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths).

6. **Check for extension hooks**: After `tasks.md` is generated, check if `app-create/extensions.yml` exists in the project root.
   - If it exists, read it and look for entries under the `hooks.after_tasks` key.
   - Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
   - For each executable hook, output the following based on its `optional` flag:
     - **Optional hook** (`optional: true`):
       ```
       ## Extension Hooks

       **Optional Hook**: {extension}
       Command: `/{command}`
       Description: {description}

       Prompt: {prompt}
       To execute: `/{command}`
       ```
     - **Mandatory hook** (`optional: false`):
       ```
       ## Extension Hooks

       **Automatic Hook**: {extension}
       Executing: `/{command}`
       EXECUTE_COMMAND: {command}
       ```
   - If no hooks are registered or `app-create/extensions.yml` does not exist, skip silently.

Context for task generation: $ARGUMENTS

The `tasks.md` should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox).
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order.
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks).
4. **[Story] label**: REQUIRED for user story phase tasks only.
   - Format: `[US1]`, `[US2]`, `[US3]`, etc. (maps to user stories from `spec.md`).
   - Setup phase: NO story label.
   - Foundational phase: NO story label.  
   - User Story phases: MUST have story label.
   - Polish phase: NO story label.
5. **Description**: Clear action with exact file path.

**Examples**:

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase.
   - Map all related components to their story:
     - Models needed for that story.
     - Services needed for that story.
     - Interfaces/UI needed for that story.
     - If tests requested: Tests specific to that story.
   - Mark story dependencies (most stories should be independent).

2. **From Contracts**:
   - Map each interface contract $\rightarrow$ to the user story it serves.
   - If tests requested: Each interface contract $\rightarrow$ contract test task [P] before implementation in that story's phase.

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it.
   - Relationships $\rightarrow$ service layer tasks in appropriate story phase.

4. **From Setup/Infrastructure**:
   - Shared infrastructure $\rightarrow$ Setup phase (Phase 1).
   - Foundational/blocking tasks $\rightarrow$ Foundational phase (Phase 2).
   - Story-specific setup $\rightarrow$ within that story's phase.

### Phase Structure

- **Phase 1**: Setup (project initialization).
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories).
- **Phase 3+**: User Stories in priority order (P1, P2, P3...).
  - Within each story: Tests (if requested) $\rightarrow$ Models $\rightarrow$ Services $\rightarrow$ Endpoints $\rightarrow$ Integration.
  - Each phase should be a complete, independently testable increment.
- **Final Phase**: Polish & Cross-Cutting Concerns.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories can then proceed in parallel (if staffed) or sequentially in priority order (P1 $\rightarrow$ P2 $\rightarrow$ P3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable.
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable.

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation.
- Models before services.
- Services before endpoints.
- Core implementation before integration.
- Story complete before moving to next priority.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- All Foundational tasks marked [P] can run in parallel (within Phase 2).
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows).
- All tests for a user story marked [P] can run in parallel.
- All models within a story marked [P] can run in parallel.
- Different user stories can be worked on in parallel by different team members.

### Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Test User Story 1 independently.
5. Deploy/demo if ready.

### Incremental Delivery

1. Complete Setup + Foundational $\rightarrow$ Foundation ready.
2. Add User Story 1 $\rightarrow$ Test independently $\rightarrow$ Deploy/Demo (MVP!).
3. Add User Story 2 $\rightarrow$ Test independently $\rightarrow$ Deploy/Demo.
4. Add User Story 3 $\rightarrow$ Test independently $\rightarrow$ Deploy/Demo.
5. Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1.
   - Developer B: User Story 2.
   - Developer C: User Story 3.
3. Stories complete and integrate independently.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Verify tests fail before implementing.
- Commit after each task or logical group.
- Stop at any checkpoint to validate story independently.
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence.
