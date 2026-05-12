from lexical import LexicalAnalyzer
from syntactic import SyntacticAnalyzer

from logs import logger


class Parser:
    def __init__(self, code: str):
        self.code = code
        print(f"Initializing parser with code: {code!r}")
        self.position = 0
        self.lexical_analyzer = LexicalAnalyzer(code)
        self.syntactic_analyzer = None

    def parse(self):
        tokens = self.lexical_analyzer.analyze()
        print(f"Lexical analysis produced tokens: {tokens}")
        self.syntactic_analyzer = SyntacticAnalyzer(tokens)
        return self.syntactic_analyzer.parse()
