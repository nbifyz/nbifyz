# Rules for Finding and Reading Files on Windows (Git Bash)

## The Problem
When finding or reading files via Git Bash on Windows, paths often get mangled due to differences between Unix slashes (`/`) and Windows backslashes (`\`). Standard commands like `cat`, `grep`, or `find` can freeze the terminal if they accidentally hit binary files, massive `node_modules` folders, or read files with incorrect encoding (like UTF-16 on Windows).

## Mandatory Rules for AI Agent

### 1. ABSOLUTE PREFERENCE: Use Python for Target File Reading
Do not use raw `cat` or `head` for files where encoding might be broken (e.g., system files or files edited by Windows tools). Use the Python interpreter to read text safely with explicit encoding handling.

**Template:**
```bash
python -c "import pathlib; print(pathlib.Path('your/file/path.py').read_text(encoding='utf-8', errors='ignore'))"
```

### 2. SAFE FINDING: Universal File Search
Standard Windows paths and Git Bash `find` can conflict. To find a file by name safely without getting stuck in infinite loops or permissions issues, use `find` with explicitly specified forward slashes and ignored system directories.

*   Always use forward slashes `./` for the starting point.
*   Exclude massive dependency folders (`node_modules`, `.git`, `vendor`) to prevent terminal freezing.

**Template:**
```bash
find . -type d \( -name "node_modules" -o -name ".git" -o -name "vendor" \) -prune -o -name "*target_file*.py" -print
```

### 3. SAFE GREP: Searching Content Inside Files
When searching for text or functions inside files on Windows, `grep` can fail or output raw binary garbage if it hits lockfiles or compiled binaries. Use `ripgrep` (`rg`) if available, or force `grep` to treat inputs correctly.

*   Always ignore binary files with `--binary-files=without-match`.
*   Exclude heavy directories using `--exclude-dir`.

**Template:**
```bash
grep -rn --binary-files=without-match --exclude-dir={node_modules,.git,vendor,dist} "your_search_term" .
```

### 4. READING GIANT FILES (> 200 lines): Streamlined Inspection
Never use a plain `cat` on a massive file or log output. It floods the terminal, consumes agent context limits, and causes Git Bash buffer truncation. Use chunked reading.

*   Use `head` and `tail` to see the structure first.
*   Use `sed` to extract specific line ranges.

**Templates:**
```bash
# Read specific lines (e.g., lines 100 to 150) safely:
sed -n '100,150p' path/to/large_file.py

# Check only the beginning and end:
head -n 20 path/to/file.log && echo "---" && tail -n 20 path/to/file.log
```

### 5. Windows Path and Encoding Verification Step
Before processing file contents, ensure the path layout is resolved and hidden Windows carriage returns (`\r`) won't break your regex logic.

```bash
# Check file type and encoding format before deep analysis:
file path/to/target_file.py

# Count lines safely without printing the code:
wc -l path/to/target_file.py
```
