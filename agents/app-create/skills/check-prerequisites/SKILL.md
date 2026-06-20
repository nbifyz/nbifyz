# SKILL: check-prerequisites

## When to Use
Use this skill at the start of any phase that requires existing design artifacts (e.g., `/speckit.plan`, `/speckit.tasks`, `/speckit.analyze`, or `/speckit.implement`) to ensure all necessary files are present and the environment is correctly set up.

## Procedure Steps

1.  **Validate Environment**: Confirm that you are currently working on a valid feature branch.
2.  **Verify Feature Directory**: Ensure the active feature directory exists in the workspace.
3.  **Check Mandatory Files**: Verify that `plan.md` (the implementation plan) is present in the feature directory.
4.  **Conditional Check for Tasks**: If the current workflow requires tasks (e.g., during implementation), verify that `tasks.md` exists.
5.  **Compile Available Documents List**: Scan the feature directory and compile a list of all available design artifacts, including:
    - `research.md`
    - `data-model.md`
    - `contracts/` (directory)
    - `quickstart.md`
    - `tasks.md` (if requested)
6.  **Return Metadata**: Provide the following information for subsequent steps:
    - `FEATURE_DIR`: The absolute path to the feature directory.
    - `AVAILABLE_DOCS`: A list of all identified design artifacts.

## Pitfalls

- **Wrong Branch**: Running this skill on a main or development branch will result in an error, as it cannot find the required feature context.
- **Missing Plan**: Attempting to generate tasks or implement without first running `/speckit.plan` (which creates `plan.md`) will cause failure.
- **Incomplete Artifacts**: Relying on a document that is listed but empty or corrupted.

## Verification Steps

- [ ] The returned `FEATURE_DIR` path is absolute and correct.
- [ ] The `AVAILABLE_DOCS` list accurately reflects the files actually present in the directory.
- [ ] If `-RequireTasks` was requested, the presence of `tasks.md` is confirmed.
