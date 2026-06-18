# Context Analysis: app-creator

## 1. Current Structure
The directory `C:/Project/Athenta/test5/Prj/app-creator/` currently contains hidden directories `./pi` and `./specify` which hold essential assets for the agents.

### Existing Folders:
- `agents/`: Agent definition files (`*.info.md`).
- `prompts/`: Prompt templates.
- `skills/`: Skill definitions.

### Hidden/External Dependencies (to be merged):
- `./prompts/`: Contains `speckit.*.md` prompt templates.
- `./integrations/`: Contains integration manifests and scripts.
- `./memory/`: Contains the project constitution (`constitution.md`).
- `./scripts/`: Contains bash and powershell utility scripts.
- `./templates/`: Contains markdown templates for agents.

## 2. Identified Broken/External References
Most files in `agents/` and `prompts/` use relative paths that point to the `./pi` or `./specify` directories. These will break once the folder is moved to a standalone location (`C:\Users\user\./pi\agent\agents`).

**Key references found:**
- `./extensions.yml` (referenced in almost all agent files)
- `./memory/constitution.md` (referenced in `analyze.info.md`, `constitution.info.md`, etc.)
- `./scripts/bash/check-prerequisites.sh` (referenced in `analyze.info.md`, `checklist.info.md`, etc.)
- `./templates/*.md` (referenced in `checklist.info.md`, `specify.info.md`, etc.)
- `./prompts/speckit.*.md` (referenced in `pi.manifest.json`)
- `./integrations/pi/scripts/update-context.sh` (referenced in `integration.json`)

## 3. Proposed Migration Plan
To make the `app-creator` folder self-contained, we will:

1. **Merge Files**:
   - Move `./prompts/*` $\rightarrow$ `prompts/`
   - Move `./integrations/*` $\rightarrow$ `integrations/`
   - Move `./memory/*` $\rightarrow$ `memory/`
   - Move `./scripts/*` $\rightarrow$ `scripts/`
   - Move `./templates/*` $\rightarrow$ `templates/`
   - Move `./extensions.yml` $\rightarrow$ `./extensions.yml`

2. **Refactor Paths**:
   Update all files to use relative paths based on the new structure. 
   Example:
   - Old: `./memory/constitution.md`
   - New: `./memory/constitution.md`
   - Old: `./prompts/speckit.analyze.md`
   - New: `./prompts/speckit.analyze.md`

3. **Update Manifests**:
   Update `integration.json` and any manifest files to reflect the new paths.

## 4. Risks & Constraints
- **Path Complexity**: Some scripts might rely on being run from a specific directory (e.g., "repo root"). We must ensure they work when called from within the new standalone folder structure.
- **Shell Compatibility**: Ensure bash/powershell scripts use correct relative paths for internal calls.
