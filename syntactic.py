from abstract_syntax_tree import Final, Identifier, JoinStatement, LogicalOperator, SelectStatement
from lexical import TokenizedQuery

from logs import logger


class SyntacticAnalyzer:
    def __init__(self, tokens: TokenizedQuery):
        self.tokens: TokenizedQuery = tokens
        self.current: int = 0

    def _format_syntax_error(self, message: str, expected_type=None, expected_value=None):
        token = self._peek()

        expected_parts = []
        if expected_type is not None:
            expected_parts.append(f"type={expected_type}")
        if expected_value is not None:
            expected_parts.append(f"value={expected_value!r}")
        expected_text = f" (expected: {', '.join(expected_parts)})" if expected_parts else ""

        if token is None:
            return (
                f"{message}{expected_text}. "
                f"Failed at token index {self.current}: reached end of input (EOF)."
            )

        return (
            f"{message}{expected_text}. "
            f"Failed at token index {self.current}: "
            f"found type={token.type}, value={token.value!r}."
        )

    def _peek(self):
        if self.current < len(self.tokens.tokens):
            return self.tokens.tokens[self.current]
        return None

    def is_at_end(self):
        return self._peek() is None

    def _advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.tokens.tokens[self.current - 1]

    def consume(self, expected_type, message, expected_value=None):
        if self._peek() and self._peek().type == expected_type:
            if expected_value is None or self._peek().value == expected_value:
                return self._advance()
        raise SyntaxError(
            self._format_syntax_error(
                message,
                expected_type=expected_type,
                expected_value=expected_value,
            )
        )

    def parse(self):
        return self._select_statement()

    def _select_statement(self):
        logger.debug("Parsing SELECT statement")
        self.consume('KEYWORD', "Expected 'SELECT' at the beginning of the query", expected_value='SELECT')
        columns: list[Identifier] = self._column_list()
        logger.debug(f"Parsed columns: {[col for col in columns]}")
        if not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'FROM':
            logger.debug("Parsing FROM clause")
            self.consume('KEYWORD', "Expected 'FROM' after column list", expected_value='FROM')
            table: Identifier = self.consume('ID', "Expected table name after 'FROM'")
            joins: list[JoinStatement] = []
            where: LogicalOperator | None = None
            if not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'JOIN':
                logger.debug("Parsing JOIN clause(s)")
                joins: list[JoinStatement] = self._parse_joins()
                logger.debug(f"Parsed joins: {joins}")
            if not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'WHERE':
                logger.debug("Parsing WHERE clause")
                # self.consume('KEYWORD', "Expected 'WHERE'", expected_value='WHERE')
                where = self._where_clause()
                logger.debug(f"Parsed WHERE condition: {where}")
        self.consume('END', "Expected end of query", expected_value=';')
        return SelectStatement(
            columns=columns,
            table=table,
            joins=joins,
            where=where
        )

    def _column_list(self):
        columns = [self.consume('ID', "Expected column name")]
        while self._peek() and self._peek().type == 'COMMA':
            self._advance()  # consume the comma
            columns.append(self.consume('ID', "Expected column name after ','"))
        return columns

    def _join_statement(self):
        self.consume('KEYWORD', "Expected 'JOIN'", expected_value='JOIN')
        table: Identifier = self.consume('ID', "Expected table name after 'JOIN'")
        on: LogicalOperator | None = None
        if not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'ON':
            self.consume('KEYWORD', "Expected 'ON'", expected_value='ON')
            on: LogicalOperator = self._condition()
        return JoinStatement(
            table=table,
            on=on
        )

    def _logical_operator(self):
        left = self._comparison()
        while not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'AND':
            operator = self.consume('KEYWORD', "Expected logical operator", expected_value='AND')
            right = self._comparison()
            left = LogicalOperator(
                operator=operator.value,
                left=left,
                right=right
            )
        return left

    def _parse_joins(self):
        joins = []
        while not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value == 'JOIN':
            joins.append(self._join_statement())
        return joins

    def _on_clause(self):
        pass

    def _where_clause(self):
        self.consume('KEYWORD', "Expected 'WHERE'", expected_value='WHERE')
        return self._condition()

    def _condition(self) -> LogicalOperator:
        left = self._term()

        while not self.is_at_end() and self._peek().type == 'KEYWORD' and self._peek().value.upper() == 'AND':
            operator = self.consume('KEYWORD', "Expected logical operator", expected_value='AND')
            right = self._term()
            left = LogicalOperator(
                operator=operator.value,
                left=left,
                right=right
            )
        return left

    def _term(self):
        if not self.is_at_end() and self._peek().value == '(':
            self.consume('OP', "Expected '('", expected_value='(')
            expr = self._condition()
            # expr = self._term()
            self.consume('OP', "Expected ')'", expected_value=')')
            return expr
        else:
            return self._comparison()

    def _comparison(self) -> LogicalOperator:
        left = self._parse_identifier()
        operator = self.consume('OP', "Expected comparison operator", expected_value=None)
        right_token = self._peek()
        if right_token.type == 'ID':
            right = self._parse_identifier()
        elif right_token.type in ('NUMBER', 'STRING'):
            right = Final(value=self.consume(right_token.type, "Expected literal value").value)
        else:
            raise SyntaxError(self._format_syntax_error("Expected identifier or literal after comparison operator"))
        return LogicalOperator(
            operator=operator.value,
            left=left,
            right=right
        )

    def _parse_identifier(self):
        value = self.consume('ID', "Expected identifier").value

        if self._peek() and self._peek().value == '.':
            self._advance()  # consume the dot
            column = self.consume('ID', "Expected column name after '.'").value
            return Identifier(name=f"{value}.{column}")
        return Identifier(name=value)
