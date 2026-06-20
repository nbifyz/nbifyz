# SKILL: setup-plan

## When to Use
Use this skill at the beginning of the implementation planning phase (after `/speckit.specify` is complete) to initialize the technical plan file and prepare the workspace for design artifacts.

## Procedure Steps

1.  **Validate Environment**: Ensure you are currently on a valid feature branch.
2.  **Prepare Workspace**: Create the feature directory if it does not already exist.
3.  **Initialize Plan File**: 
    - Locate the `plan-template.md` in the project templates directory.
    - Copy the template content to the implementation plan file (e.g., `app-create/specs/<branch_name>/plan.md`).
4.  **Return Metadata**: Provide the following information for subsequent planning steps:
    - `FEATURE_SPEC`: Path to the feature specification (`spec.md`).
    - `IMPL_PLAN`: Path to the newly created implementation plan file.
    - `SPECS_DIR`: The directory containing all feature artifacts.
    - `BRANCH`: The current active branch name.

## Pitfalls

- **Non-Feature Branch**: Running this skill on a main or development branch instead of a dedicated feature branch will fail to set up the correct workspace.
- **Missing Template**: If the `plan-template.md` is missing, the skill may create an empty file instead of a structured plan.
- **Path Mismatch**: Failing to use absolute paths for metadata can cause downstream agents to fail when looking for artifacts.

## Verification Steps

- [ ] The implementation plan file (`IMPL_PLAN`) exists and contains the template structure.
- [ ] All returned metadata (paths and branch name) are valid and absolute.
- [ ] The feature directory is correctly initialized.
