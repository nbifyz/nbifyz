---
description: Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.
handoffs: 
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before clarification)**:
- Check if `app-create/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_clarify` key.
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

Goal: Detect and reduce ambiguity or missing decision points in the active feature specification and record the clarifications directly in the spec file.

Note: This clarification workflow is expected to run (and be completed) BEFORE invoking `/speckit.plan`. If the user explicitly states they are skipping clarification (e.g., exploratory spike), you may proceed, but must warn that downstream rework risk increases.

Execution steps:

1. Run `check-prerequisites` skill/command with `-Json -PathsOnly` from repo root. Parse minimal JSON payload fields:
   - `FEATURE_DIR`
   - `FEATURE_SPEC`
   - If JSON parsing fails, abort and instruct user to re-run `/speckit.specify` or verify feature branch environment.

2. Load the current spec file. Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing. Produce an internal coverage map used for prioritization (do not output raw map unless no questions will be asked).

   Taxonomy:
   - Functional Scope & Behavior (Goals, scope, personas)
   - Domain & Data Model (Entities, attributes, relationships, lifecycle)
   - Interaction & UX Flow (Journeys, error/empty states, accessibility)
   - Non-Functional Quality Attributes (Performance, scalability, reliability, observability, security)
   - Integration & External Dependencies (APIs, failure modes, formats)
   - Edge Cases & Failure Handling (Negative scenarios, rate limiting, conflicts)
   - Constraints & Tradeoffs (Technical constraints, rejected alternatives)
   - Terminology & Consistency (Glossary, canonical terms)
   - Completion Signals (Acceptance criteria testability)

3. Generate (internally) a prioritized queue of candidate clarification questions (maximum 5). Do NOT output them all at once. Apply these constraints:
    - Maximum of 5 total questions across the whole session.
    - Each question must be answerable with EITHER:
       - A short multiple‑choice selection (2–5 distinct, mutually exclusive options), OR
       - A one-word / short‑phrase answer (explicitly constrain: "Answer in <=5 words").
    - Only include questions whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, or compliance validation.
    - Prioritize by (Impact * Uncertainty) heuristic.

4. Sequential questioning loop (interactive):
    - Present EXACTLY ONE question at a time.
    - For multiple‑choice questions:
       - **Analyze all options** and determine the **most suitable option** based on best practices and risk reduction.
       - Present your **recommended option prominently**: `**Recommended:** Option [X] - <reasoning>`
       - Render all options as a Markdown table:

       | Option | Description |
       |--------|-------------|
       | A | <Option A description> |
       | B | <Option B description> |
       | C | <Option C description> |
       | Short | Provide a different short answer (<=5 words) |

       - After the table, add: `You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.`
    - For short‑answer style:
       - Provide your **suggested answer**: `**Suggested:** <your proposed answer> - <brief reasoning>`
       - Output: `Format: Short answer (<=5 words). You can accept the suggestion by saying "yes" or "suggested", or provide your own answer.`
    - After the user answers:
       - If the user replies with "yes", "recommended", or "suggested", use your recommendation/suggestion.
       - Validate the answer (mapping to option or <=5 words).
       - Record it in working memory and move to the next question.
    - Stop when: All critical ambiguities resolved, 5 questions reached, or user signals completion ("done").

5. Integration after EACH accepted answer (incremental update approach):
    - Maintain an in-memory representation of the spec plus raw file contents.
    - For the first integrated answer:
       - Ensure a `## Clarifications` section exists in the spec file.
       - Create a `### Session YYYY-MM-DD` subheading.
    - Append a bullet line: `- Q: <question> → A: <final answer>`.
    - Immediately apply the clarification to the most appropriate section(s):
       - Functional ambiguity $\rightarrow$ Update/add in Functional Requirements.
       - User interaction / roles $\rightarrow$ Update User Stories or Actors.
       - Data shape / entities $\rightarrow$ Update Data Model (fields, types, relationships).
       - Non-functional constraint $\rightarrow$ Update Success Criteria (convert vague to metric).
       - Edge case $\rightarrow$ Add/update in Edge Cases section.
    - Save the spec file AFTER each integration (atomic overwrite).
    - Preserve formatting and heading hierarchy.

6. Validation (performed after EACH write plus final pass):
   - Clarifications session contains exactly one bullet per accepted answer.
   - Total asked questions $\le$ 5.
   - Updated sections contain no lingering vague placeholders the new answer was meant to resolve.
   - No contradictory earlier statement remains.
   - Markdown structure valid; only allowed new headings: `## Clarifications`, `### Session YYYY-MM-DD`.

7. Write the updated spec back to the `FEATURE_SPEC` path.

8. Report completion:
   - Number of questions asked & answered.
   - Path to updated spec.
   - Sections touched.
   - Coverage summary table (Status: Resolved, Deferred, Clear, Outstanding).
   - Suggested next command.

Behavior rules:

- If no meaningful ambiguities found, respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding.
- If spec file missing, instruct user to run `/speckit.specify` first.
- Never exceed 5 total asked questions.
- Avoid speculative tech stack questions unless they block functional clarity.
- Respect user early termination signals ("stop", "done").

Context for prioritization: $ARGUMENTS

## Post-Execution Checks

**Check for extension hooks (after clarification)**:
Check `app-create/extensions.yml` for `hooks.after_clarify`.
- If it exists, read it and look for entries under the `hooks.after_clarify` key.
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
