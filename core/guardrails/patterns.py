"""Padrões de payloads que não devem chegar às regras de negócio."""

SQL_INJECTION_PATTERNS = (
    r"\bselect\b",
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\bunion\b",
    r"\balter\b",
    r"\bexec(?:ute)?\b",
    r"\bxp_cmdshell\b",
    r"--",
    r"(?:'|\")\s*or\s+(?:1\s*=\s*1|'[^']*'\s*=\s*'[^']*')",
)

XSS_PATTERNS = (
    r"<\s*script\b",
    r"\bjavascript\s*:",
    r"<\s*iframe\b",
    r"<\s*embed\b",
    r"<\s*object\b",
    r"\bonerror\s*=",
    r"\bonclick\s*=",
)

PROMPT_INJECTION_PATTERNS = (
    r"\bignore previous instructions?\b",
    r"\bignore all instructions?\b",
    r"\bsystem override\b",
    r"\bdeveloper mode\b",
    r"\bjailbreak\b",
    r"\bsudo mode\b",
    r"\bact as\b",
    r"\byou are now\b",
    r"\breveal (?:the )?system prompt\b",
    r"\bignore (?:suas|as) instrucoes\b",
    r"\bmostre (?:o )?prompt (?:do )?sistema\b",
)
