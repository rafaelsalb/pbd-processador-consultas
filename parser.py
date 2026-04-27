from lexical import LexicalAnalyzer
from syntactic import SyntacticAnalyzer


class Parser:
    def __init__(self, code: str):
        self.code = code
        self.position = 0
        self.lexical_analyzer = LexicalAnalyzer(code)
        self.syntactic_analyzer = None

    def parse(self):
        tokens = self.lexical_analyzer.analyze()
        print(self.code)
        print(tokens)
        self.syntactic_analyzer = SyntacticAnalyzer(tokens)
        return self.syntactic_analyzer.parse()
