---
description: Create or update the feature specification from a natural language feature description.
handoffs: 
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
    send: true
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before specification)**:
- Check if `app-create/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_specify` key.
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

The text the user typed after `/speckit.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords.
   - Create a 2-4 word short name (e.g., "user-auth", "fix-payment-timeout").
   - Use action-noun format when possible.

2. **Create the feature branch**:
   - Use the skill `create-feature-branch` to run the underlying logic of `.specify/scripts/powershell/create-new-feature.ps1`.
   - Check `app-create/init-options.json` (or original `.specify/init-options.json`) for `branch_numbering` value:
     - If `"timestamp"`, use the timestamp flag.
     - If `"sequential"` or absent, use default numbering.
   - **IMPORTANT**: The skill will return a JSON object containing `BRANCH_NAME` and `SPEC_FILE`. Use these paths for all subsequent steps.

3. **Load Template**:
   - Read `app-create/templates/spec-template.md` to understand required sections.

4. **Execution Flow**:
    1. Parse user description from Input.
    2. Extract key concepts (actors, actions, data, constraints).
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards.
       - Mark with `[NEEDS CLARIFICATION: specific question]` only if critical.
       - **LIMIT**: Maximum 3 `[NEEDS CLARIFICATION]` markers total.
    4. Fill User Scenarios & Testing section (ensure they are independent and testable).
    5. Generate Functional Requirements (must be testable).
    6. Define Success Criteria (measurable, technology-agnostic outcomes).
    7. Identify Key Entities.

5. **Write Specification**:
   - Write the completed content to the `SPEC_FILE` path obtained from the branch creation step, using the template structure.

6. **Specification Quality Validation**:
   - **a. Create Checklist**: Generate a checklist file at `{FEATURE_DIR}/checklists/requirements.md` using the `app-create/templates/checklist-template.md`.
   - **b. Run Validation Check**: Review the spec against the checklist items.
   - **c. Handle Results**:
      - If all pass: Proceed to step 7.
      - If items fail (excluding clarifications): Update the spec and re-validate (max 3 iterations).
      - If `[NEEDS CLARIFICATION]` markers remain:
        1. Extract them (max 3).
        2. Present them to the user in a structured Markdown table with "Suggested Answers" (Option A, B, C, Custom).
        3. **Wait for user response**.
        4. Update spec with chosen answers and re-validate.

7. **Report Completion**:
   - Output: branch name, spec file path, checklist results, and readiness for `/speckit.clarify` or `/speckit.plan`.

8. **Check for extension hooks (after specification)**:
   - Check `app-create/extensions.yml` for `hooks.after_specify`.
   - Execute mandatory/optional hooks as defined.

## Key rules

- Use absolute paths within the `app-create` context.
- Do not include implementation details (frameworks, specific APIs) in the specification.
- Focus on **WHAT** and **WHY**, not **HOW**.
- Ensure all requirements are testable and success criteria are measurable.
