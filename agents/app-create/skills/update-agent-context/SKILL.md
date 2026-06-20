# SKILL: update-agent-context

## When to Use
Use this skill when you need to synchronize the technical stack (language, framework, database) and project metadata from a `plan.md` file into the agent's specific context files (e.g., `CLAUDE.md`, `QWEN.md`, `.cursor/rules/specify-rules.mdc`). This ensures that all AI agents working on the feature are aware of the current technical decisions and project state.

## Procedure Steps

1.  **Identify Target Agent**: Determine which agent's context needs updating (e.g., `claude`, `qwen`, `cursor-agent`, or `all` to update every existing file).
2.  **Locate Plan File**: Ensure the current feature's `plan.md` is available in the active workspace.
3.  **Execute Update**: Run the corresponding command (e.g., `.specify/scripts/powershell/update-agent-context.ps1 -AgentType <type>`) to parse the plan and update the target file(s).
4.  **Verify Update**: Check the updated context file to ensure:
    - The technology stack matches the `plan.md`.
    - The branch name is correctly reflected.
    - No syntax errors were introduced in the Markdown/YAML content.

## Pitfalls

- **Missing Plan File**: Attempting to update context when no `plan.md` exists for the current feature will result in an error.
- **Incorrect Agent Type**: Providing a type that doesn't match any known agent (e.g., typo in `claude`) will fail to update anything.
- **Incomplete Plan**: If the `plan.md` has not been fully filled out (contains many `NEEDS CLARIFICATION` markers), the updated context might be incomplete or inaccurate.

## Verification Steps

- [ ] The target agent file (e.g., `CLAUDE.md`) exists and was modified.
- [ ] The technology stack in the agent file matches the `plan.md`.
- [ ] The branch name is correctly included in the context.
- [ ] No syntax errors or broken Markdown formatting in the updated file.
