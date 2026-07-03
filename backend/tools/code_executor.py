"""
tools/code_executor.py
Sandboxed Python code execution tool.
Runs code in a restricted environment with a timeout.
"""

from langchain_core.tools import tool
import subprocess
import tempfile
import os
import sys
import re


# Dangerous modules blocked by import name (matched as whole words)
_BLOCKED_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket",
    "requests", "importlib", "builtins", "pathlib",
    "ctypes", "multiprocessing", "threading",
}
# Dangerous builtins matched as function calls
_BLOCKED_BUILTINS = {"__import__", "open", "exec", "eval", "compile", "globals", "locals"}


def _is_blocked(code: str):
    """Return the offending pattern string if code should be blocked, else None."""
    # Match: import X  /  import X as Y  /  from X import ...
    for m in re.finditer(r'(?:^|\s)(?:import|from)\s+(\w+)', code, re.MULTILINE):
        mod = m.group(1)
        if mod in _BLOCKED_MODULES:
            return f"import {mod}"
    # Match dangerous builtins used as calls: open(...), eval(...), etc.
    for b in _BLOCKED_BUILTINS:
        if re.search(r'\b' + re.escape(b) + r'\s*\(', code):
            return b + "()"
    return None


@tool
def execute_code(code: str) -> str:
    """
    Execute Python code and return the output.
    Use this for: math calculations, data analysis, algorithm problems,
    generating plots descriptions, or verifying logic.
    Input: valid Python code as a string.
    Output: stdout output or error message.
    DO NOT use for file system operations or network requests.
    """
    blocked = _is_blocked(code)
    if blocked:
        return "⚠ Blocked: code contains restricted operation: '" + blocked + "'"

    # Write to temp file and run with timeout
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if error and not output:
            return "Error:\n" + error
        if error:
            return "Output:\n" + output + "\n\nWarnings:\n" + error
        return output if output else "Code ran successfully with no output."

    except subprocess.TimeoutExpired:
        return "⚠ Execution timed out (10s limit exceeded)."
    except Exception as e:
        return "⚠ Execution failed: " + str(e)
    finally:
        os.unlink(tmp_path)
