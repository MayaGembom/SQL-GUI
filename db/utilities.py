__all__ = ['execute_query']

from typing import Iterable, List

from db import filters
from db.context_manager import SqlLocalDatabaseContextManager
from db.data_structures import ColumnType


def execute_query(query: str) -> Iterable[str]:
    """
    Runs `query` on the database and yields the results one by one.

    :param query: The query to run.
    :return: Yields the results of the query.
    """
    with SqlLocalDatabaseContextManager() as cursor:
        cursor.execute(query)
        for result in cursor:
            yield result


def execute_queries(queries: Iterable[str]):
    with SqlLocalDatabaseContextManager() as cursor:
        for query in queries:
            cursor.execute(query)
            yield from cursor


def add_filters_to_query(query: str, query_filters: Iterable[filters.Filter], case_sensitive: bool) -> str:
    """
    Appends `table_filters` to `query` as a 'WHERE' statement at the end of the query.

    :param query: The base query.
    :param query_filters: The filters to add to the query.
    :param case_sensitive: Are the filters case sensitive.
    :return: The new query with the filters as 'WHERE' statement.
    """
    # Get the query version of every filter
    filters_queries: List[str] = [table_filter.get_query(case_sensitive) for table_filter in query_filters]

    if len(filters_queries) == 0:
        return query
    # Concatenate the WHERE statement and the filters to the query and return the result.
    return ' '.join((query, 'WHERE', ' AND '.join(filters_queries)))


def get_all_tables_in_database():
    """ Retrieves all the tables in the database and sorts them by name. """
    query = """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'; """
    return sorted([i[0] for i in execute_query(query)])


def sql_type_to_enum_type(column_type: str) -> ColumnType:
    """ Converts the given column type from a sql format (e.g. INTEGER, VARCHAR, etc…)
    to the appropriate ColumnType instance. """
    # If the type is a varchar (text)
    if column_type.lower().startswith('nvarchar'):
        return ColumnType.Text

    return ColumnType.Numeric
