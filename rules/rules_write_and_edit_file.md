# Rules for Writing and Editing Files on Windows (Git Bash)

## The Problem
When writing or editing files via Git Bash on Windows using `cat << 'EOF'` or standard `sed`, files often get truncated, throw "unexpected EOF", or break due to incorrect slash/quote escaping. This is caused by CRLF (\r\n) line endings and Bash parsing special characters.

## Mandatory Rules for AI Agent

### 1. ABSOLUTE PREFERENCE: Use Python for File Writing
Do not use `cat << 'EOF'` for large or critical files. Instead, use the Python interpreter to write files directly. This bypasses Bash limitations and handles encodings flawlessly.

**Template:**
```bash
python -c "
import pathlib
code = '''# Your code here
# Keep formatting exact
'''
pathlib.Path('your/file/path.py').write_text(code, encoding='utf-8')
"
```

### 2. EDITING EXISTING FILES: Use `sd` Safely
When using `sd` (search and replace) in Git Bash on Windows, you must protect regex patterns and replacement strings from being mangled by the shell.

*   Always wrap both the search pattern and the replacement in **single quotes** (`'`).
*   If your find/replace text contains single quotes, escape them as `'\''` or temporarily use the Python approach to rewrite the file section.
*   Remember that `sd` modifies files in-place by default.

**Template:**
```bash
sd 'pattern_to_find' 'replacement_text' your/file/path.py
```

### 3. FALLBACK: Safe Heredoc (If you must use `cat`)
If you are forced to use `cat`, you must clean Windows carriage returns (`\r`) in flight and ensure the EOF tag is perfectly isolated.

*   Always wrap the initial tag in single quotes: `<< 'PYEOF'`
*   Pipe the output through `tr -d '\r'` to remove hidden Windows line endings.
*   The closing tag `PYEOF` must be on a completely new line, with NO leading or trailing spaces/tabs.

**Template:**
```bash
cat << 'PYEOF' | tr -d '\r' > your/file/path.py
# Your code here
PYEOF
```

### 4. FOR LARGE FILES (> 150 lines): Use Base64
If the file is long, Git Bash buffer will truncate the text. Encode the content into Base64 locally, then decode it on the target machine.

**Template:**
```bash
echo "BASE64_ENCODED_STRING_HERE" | base64 -d > your/file/path.py
```

### 5. Verification Step
After writing or editing any file, always verify its integrity by checking the last line or running a syntax check.
```bash
tail -n 5 your/file/path.py
python -m py_compile your/file/path.py
```
