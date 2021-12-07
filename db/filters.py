__all__ = ['get_filter']

from abc import ABC, abstractmethod
from typing import Dict, Sequence, Type

from db import operators
from db.data_structures import ColumnData, ColumnType, Operator

_filter_types_by_column_type: Dict[ColumnType, Type['Filter']] = dict()


class Filter(ABC):

    def __init__(self, column_name: str):
        self.column_name = column_name
        self._operator = self.operators[0]  # default to the first operator
        self._value = ''

    def __init_subclass__(cls, column_type: ColumnType = None, **kwargs):
        super().__init_subclass__(**kwargs)
        _filter_types_by_column_type[column_type] = cls

    def get_query(self, case_sensitive: bool) -> str:
        """ Returns the filter formatted to SQL query """
        return self.operator.get_query(self.column_name, self.value, case_sensitive)

    # region Properties
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        if self.operator in (operators.NONE_OPERATOR, operators.NOT_NONE_OPERATOR):
            self._value = ""
            return
        if len(value) == 0:
            raise ValueError(f"Value can't be an empty string!")
        if not self._validate_value(value) and self.operator is not operators.IN_OPERATOR:
            raise ValueError(f'Invalid value {value!r}!')

        self._value = value

    @property
    def operator(self) -> Operator:
        return self._operator

    @operator.setter
    def operator(self, operator: Operator):
        if operator not in self.operators:
            raise ValueError(f'Invalid operator {operator!r}, supported operators are: {self.operators}')

        self._operator = operator

    @property
    def operators(self) -> Sequence[Operator]:
        """ Sequence of all the operators this filter supports """
        return operators.EQUALS_OPERATOR, operators.NOT_EQUALS_OPERATOR, operators.IN_OPERATOR, \
               operators.GREATER_THAN_OPERATOR, operators.LESS_THAN_OPERATOR, operators.GREATER_THAN_OR_EQUALS_OPERATOR, \
               operators.LESS_THAN_OR_EQUALS_OPERATOR, operators.NONE_OPERATOR, operators.NOT_NONE_OPERATOR

    # endregion

    def __str__(self):
        return f'{self.column_name} {self.operator.name} {self.value}'

    @abstractmethod
    def _validate_value(self, value: str):
        pass


class NumericFilter(Filter, column_type=ColumnType.Numeric):

    def _validate_value(self, value: str):
        try:
            float(value)
            return True
        except ValueError:
            return False
        # if value.isnumeric():
        #     return True
        # return False


class StringFilter(Filter, column_type=ColumnType.Text):

    def _validate_value(self, value: str):
        return len(value) > 0

    @property
    def operators(self):
        # Append operators specific to this type to the base type operators.
        return (*super().operators, operators.STARTS_WITH_OPERATOR, operators.ENDS_WITH_OPERATOR,
                operators.CONTAINS_OPERATOR, operators.LIKE_OPERATOR, operators.NOT_LIKE_OPERATOR)


def get_filter(column_data: ColumnData) -> Filter:
    """ Creates a filter instance for the given column based on its name and type. """
    filter_type = _filter_types_by_column_type[column_data.column_type]
    return filter_type(column_data.get_full_name())
