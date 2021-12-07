from db.data_structures import Operator


def _prepare_value_for_in_operator(value: str) -> str:
    values = value.split(',')
    # Wrap every value with quotes
    prepared_values = [f'"{prepared_value.strip()}"' for prepared_value in values]

    return ', '.join(prepared_values)


def simple_operator(column: str, value: str, case_sensitive: bool, operator: str):
    x = f'{column} {operator} {value!r}'
    if not case_sensitive:
        x += ' COLLATE NOCASE'
    return x


def like_operator(column: str, case_sensitive: bool, pattern: str):
    x = f'{column} LIKE "{pattern}"'
    return x


# Common operators
EQUALS_OPERATOR = Operator('Equals', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '='))
NOT_EQUALS_OPERATOR = Operator('Not equals', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '!='))
IN_OPERATOR = Operator('In', lambda column, value, case_sensitive: f'{column} {"COLLATE NOCASE" if not case_sensitive else ""} IN ({_prepare_value_for_in_operator(value)})')
NONE_OPERATOR = Operator('Is None', lambda column, value, _: f'{column} is NULL')
NOT_NONE_OPERATOR = Operator('Is not None', lambda column, value, _: f'{column} is not NULL')
# Numerical operators
LESS_THAN_OPERATOR = Operator('Less than', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '<'))
LESS_THAN_OR_EQUALS_OPERATOR = Operator('Less than or equals', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '<='))
GREATER_THAN_OPERATOR = Operator('Greater than', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '>'))
GREATER_THAN_OR_EQUALS_OPERATOR = Operator('Greater than or equals', lambda column, value, case_sensitive: simple_operator(column, value, case_sensitive, '>='))
# Text operators
STARTS_WITH_OPERATOR = Operator('Starts with', lambda column, value, case_sensitive: like_operator(column, case_sensitive, f'{value}%'))
ENDS_WITH_OPERATOR = Operator('Ends with', lambda column, value, case_sensitive: like_operator(column, case_sensitive, f'%{value}'))
CONTAINS_OPERATOR = Operator('Contains', lambda column, value, case_sensitive: like_operator(column, case_sensitive, f'%{value}%'))
LIKE_OPERATOR = Operator('Like', lambda column, value, case_sensitive: like_operator(column, case_sensitive, value))
NOT_LIKE_OPERATOR = Operator('Not Like', lambda column, value, _: f'{column} NOT LIKE "{value}"')
