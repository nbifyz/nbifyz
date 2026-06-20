# SKILL: create-feature-branch

## When to Use
Use this skill when you need to initialize a new feature workspace, including creating a unique branch identifier and an initial specification file based on a user's description. This is typically the first step in the `/speckit.specify` workflow.

## Procedure Steps

1.  **Determine Numbering Mode**:
    - Read `app-create/init-options.json`.
    - Identify if `branch_numbering` is `"timestamp"` or `"sequential"`.

2.  **Generate Short Name**:
    - Analyze the feature description provided by the user.
    - Extract 2-4 meaningful keywords (e.g., "add-user-auth").
    - Use an action-noun format and convert to lowercase, replacing spaces/special chars with hyphens.

3.  **Generate Branch Name**:
    - **If `sequential`**:
        - Scan `app-create/specs/` for existing directories starting with a 3-digit number (e.g., `001-`, `002-`).
        - Find the highest number and increment it by 1 (e.g., `003-`).
    - **If `timestamp`**:
        - Generate a timestamp in `YYYYMMDD-HHMMSS` format.
        - Combine with the short name: `YYYYMMDD-HHMMSS-short-name`.

4.  **Create Workspace**:
    - Create the directory: `app-create/specs/<branch_name>/`.

5.  **Initialize Specification File**:
    - Read the template from `app-create/templates/spec-template.md`.
    - Write the content of this template to `app-create/specs/<branch_name>/spec.md`.

6.  **Return Metadata**:
    - Provide the following information for subsequent agent steps:
        - `BRANCH_NAME`: The full name of the created branch.
        - `SPEC_FILE`: The absolute path to the newly created `spec.md`.

## Pitfalls

- **Incorrect Numbering**: Failing to check `init-options.json` and defaulting to a mode that contradicts user preference.
- **Duplicate Names**: Not properly incrementing sequential numbers, leading to directory collisions.
- **Template Mismatch**: Using the wrong template or failing to copy the template entirely.
- **Path Errors**: Using relative paths that don't resolve correctly within the `app-create` context.

## Verification Steps

- [ ] The directory `app-create/specs/<branch_name>/` exists.
- [ ] The file `app-create/specs/<branch_name>/spec.md` exists and is not empty.
- [ ] The content of `spec.md` matches the structure defined in `app-create/templates/spec-template.md`.
- [ ] The branch name follows the correct format (sequential or timestamp).
