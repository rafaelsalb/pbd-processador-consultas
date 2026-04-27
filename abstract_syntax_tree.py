from dataclasses import dataclass
from typing import List, Literal, Optional, Union


class ASTNode:
    pass

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class Final(ASTNode):
    value: Union[str, int, float]

@dataclass
class LogicalOperator(ASTNode):
    left: Union[Identifier, Final, "LogicalOperator"]
    operator: Literal["=", ">", "<", "<=", ">=", "<>", "AND"]
    right: Union[Identifier, Final, "LogicalOperator"]

@dataclass
class JoinStatement(ASTNode):
    table: Identifier
    on: LogicalOperator

@dataclass
class SelectStatement(ASTNode):
    columns: List[Identifier]
    table: Identifier
    joins: List[JoinStatement] = None
    where: Optional[LogicalOperator] = None
