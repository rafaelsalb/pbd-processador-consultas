from catalog import Catalog


class SemanticValidationContext:
    def __init__(self, catalog: Catalog, scope: list[str]):
        self.catalog = catalog
        self.scope = scope

    def push_to_scope(self, table_name: str):
        self.scope.append(table_name)

    def is_in_scope(self, table_name: str) -> bool:
        return table_name in self.scope
