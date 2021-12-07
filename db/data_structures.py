from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


class ColumnType(Enum):
    Numeric = auto()
    Text = auto()


@dataclass(frozen=True, eq=False)
class ColumnData:
    """ Dataclass that holds relevant data about a column in a table """
    table_name: str
    column_type: ColumnType
    title: str
    is_primary: bool

    def get_full_name(self) -> str:
        return f'{self.table_name}.{self.title}'


@dataclass(frozen=True, eq=False)
class RelatedTable:
    """ Dataclass that holds relevant data about the connection of 2 tables """
    table_name: str
    from_column: str
    to_column: str


@dataclass(frozen=True, eq=False)
class Operator:
    _name: str
    _get_as_query: Callable[[str, str, bool], str]

    @property
    def name(self):
        return self._name

    def get_query(self, column, value, case_sensitive) -> str:
        return self._get_as_query(column, value, case_sensitive)

    def __str__(self):
        return self._name
