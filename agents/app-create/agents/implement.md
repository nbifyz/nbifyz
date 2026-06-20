---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before implementation)**:
- Check if `app-create/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_implement` key.
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

1. Run `check-prerequisites` skill (based on `.specify/scripts/powershell/check-prerequisites.ps1`) from repo root and parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute.

2. **Check checklists status** (if `app-create/specs/<branch_name>/checklists/` exists):
   - Scan all checklist files in the checklists/ directory.
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`.
     - Completed items: Lines matching `- [X]` or `- [x]`.
     - Incomplete items: Lines matching `- [ ]`.
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items.
     - **FAIL**: One or more checklists have incomplete items.

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts.
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing.
     - If user says "no" or "wait" or "stop", halt execution.
     - If user says "yes" or "proceed" or "continue", proceed to step 3.

   - **If all checklists are complete**:
     - Display the table showing all checklists passed.
     - Automatically proceed to step 3.

3. Load and analyze the implementation context:
   - **REQUIRED**: Read `app-create/specs/<branch_name>/tasks.md` for the complete task list and execution plan.
   - **REQUIRED**: Read `app-create/specs/<branch_name>/plan.md` for tech stack, architecture, and file structure.
   - **IF EXISTS**: Read `app-create/specs/<branch_name>/data-model.md` for entities and relationships.
   - **IF EXISTS**: Read `app-create/specs/<branch_name>/contracts/` for API specifications and test requirements.
   - **IF EXISTS**: Read `app-create/specs/<branch_name>/research.md` for technical decisions and constraints.
   - **IF EXISTS**: Read `app-create/specs/<branch_name>/quickstart.md` for integration scenarios.

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup (e.g., `.gitignore`, `.dockerignore`, etc.) using the detected technology stack from `plan.md`.

5. Parse `tasks.md` structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish.
   - **Task dependencies**: Sequential vs parallel execution rules.
   - **Task details**: ID, description, file paths, parallel markers [P].
   - **Execution flow**: Order and dependency requirements.

6. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next.
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together.
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks.
   - **File-based coordination**: Tasks affecting the same files must run sequentially.
   - **Validation checkpoints**: Verify each phase completion before proceeding.

7. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration.
   - **Tests before code**: If required by the task or plan.
   - **Core development**: Implement models, services, CLI commands, endpoints.
   - **Integration work**: Database connections, middleware, logging, external services.
   - **Polish and validation**: Unit tests, performance optimization, documentation.

8. Progress tracking and error handling:
   - Report progress after each completed task.
   - Halt execution if any non-parallel task fails.
   - For parallel tasks [P], continue with successful tasks, report failed ones.
   - Provide clear error messages with context for debugging.
   - Suggest next steps if implementation cannot proceed.
   - **IMPORTANT**: For completed tasks, mark the task off as `[X]` in the `tasks.md` file.

9. Completion validation:
   - Verify all required tasks are completed.
   - Check that implemented features match the original specification.
   - Validate that tests pass and coverage meets requirements.
   - Confirm the implementation follows the technical plan.
   - Report final status with summary of completed work.

10. **Check for extension hooks**: After completion validation, check `app-create/extensions.yml` for `hooks.after_implement`.
    - Execute mandatory/optional hooks as defined.

Note: This command assumes a complete task breakdown exists in `tasks.md`. If tasks are incomplete or missing, suggest running `/speckit.tasks` first to regenerate the task list.
