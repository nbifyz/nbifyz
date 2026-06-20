---
description: Generate quality checklists to validate requirements completeness, clarity, and consistency after the planning phase.
handoffs: 
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

**Check for extension hooks (before checklist generation)**:
- Check if `app-create/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_checklist` key.
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

Goal: Generate a structured checklist to validate that the feature specification (`spec.md`) and implementation plan (`plan.md`) are complete, clear, and consistent before moving to task generation.

Execution steps:

1. **Load Context**:
   - Read `app-create/specs/<branch_name>/spec.md`.
   - Read `app-create/specs/<branch_name>/plan.md`.
   - Identify the feature name and branch from these files.

2. **Analyze Requirements & Plan**:
   - Scan `spec.md` for: User stories, Functional requirements, Success criteria, Assumptions, and any `[NEEDS CLARIFICATION]` markers.
   - Scan `plan.md` for: Technical context, Project structure, and implementation phases.
   - Compare the two: Does the plan actually address all requirements in the spec? Are there gaps in the technical approach?

3. **Generate Checklist Content**:
   - Use `app-create/templates/checklist-template.md` as the base structure.
   - Create categories based on the analysis (e.g., "Requirement Completeness", "Technical Feasibility", "Testability", "Consistency").
   - Generate specific, actionable checklist items for this particular feature. 
   - **CRITICAL**: Do not use generic sample items from the template. Every item must be relevant to the current feature.

4. **Write Checklist File**:
   - Save the generated checklist to `app-create/specs/<branch_name>/checklists/requirements.md`.
   - Ensure the file includes:
     - Feature Name and Branch.
     - Date of creation.
     - Link to the original `spec.md`.

5. **Report Completion**:
   - Output the path to the new checklist.
   - Provide a brief summary of the "Risk Level" detected (Low/Medium/High) based on how many gaps or ambiguities were found during analysis.
   - Suggest whether to proceed to `/speckit.tasks` or return to `/speckit.clarify`.

6. **Check for extension hooks**: After checklist generation, check `app-create/extensions.yml` for `hooks.after_checklist`.
   - Execute mandatory/optional hooks as defined.

## Key rules

- The checklist must be specific to the feature being developed.
- If many ambiguities were found in the spec, the checklist should heavily emphasize "Clarification" and "Requirement Validation".
- Ensure all paths used are absolute within the `app-create` context.
- Do not use generic placeholders; every checkbox item must be a concrete check.
