import re
from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str


class TokenizedQuery(NamedTuple):
    tokens: list[Token]

    def __str__(self):
        return ' '.join(f'{token.type}' for token in self.tokens)


class LexicalAnalyzer:
    def __init__(self, expression: str):
        self.expression = expression

    def _format_lexical_error(self, expression: str, index: int, value: str) -> str:
        line = expression.count('\n', 0, index) + 1
        last_newline = expression.rfind('\n', 0, index)
        column = index + 1 if last_newline == -1 else index - last_newline

        line_start = 0 if last_newline == -1 else last_newline + 1
        next_newline = expression.find('\n', index)
        line_end = len(expression) if next_newline == -1 else next_newline
        line_text = expression[line_start:line_end]

        pointer = ' ' * (column - 1) + '^'
        return (
            f"Lexical analysis failed at index {index} (line {line}, column {column}): "
            f"unexpected token {value!r}\n"
            f"{line_text}\n"
            f"{pointer}"
        )

    # inspirado em https://docs.python.org/3/library/re.html
    def _tokenize(self, expression: str):
        token_specification = [
            ('KEYWORD',  r'\b(?:SELECT|FROM|WHERE|JOIN|ON|AND)\b'),  # Keywords
            ('ID',       r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*'),    # Identifiers (case-sensitive), supports table.column
            ('OP',       r'[=<>]+|[()]'),
            ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
            ('STRING',   r"'([^']*)'"),     # String literal
            ('COMMA',    r','),
            ('END',      r';'),            # Statement terminator
            ('SKIP',     r'[ \t\n]+'),       # Skip over spaces, tabs and newlines
            ('MISMATCH', r'.'),             # Any other character
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

        for mo in re.finditer(tok_regex, expression, re.IGNORECASE):
            # print(mo.groups())
            kind = mo.lastgroup
            value = mo.group(0)
            index = mo.start()
            # print(mo, kind, value)
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'KEYWORD':
                value = value.upper()
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(self._format_lexical_error(expression, index, value))
            yield Token(kind, value)

    def analyze(self):
        tokens = [token for token in self._tokenize(self.expression)]
        return TokenizedQuery(tokens)
