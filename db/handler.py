__all__ = ['SqlLiteHandler']

from typing import Iterable, Iterator, List, Sequence, Tuple

from db import utilities
from db.data_structures import ColumnData, RelatedTable
from db.filters import Filter


class SqlLiteHandler:
    """ Singleton class that provides methods to retrieve data from sqlite database """
    _instance: 'SqlLiteHandler' = None

    def __init__(self):
        self._tables_names = utilities.get_all_tables_in_database()
        self.last_data_retrieve_query = ''

    @staticmethod
    def get_instance() -> 'SqlLiteHandler':
        """ Returns the single instance of the class or create an instance if it is the first time """
        if not SqlLiteHandler._instance:
            SqlLiteHandler._instance = SqlLiteHandler()

        return SqlLiteHandler._instance

    @property
    def table_names(self) -> Sequence[str]:
        """ The names of all the tables in the database """
        return self._tables_names

    def get_columns_for(self, table_name: str) -> Sequence[ColumnData]:
        """
        Retrieves the data about the columns in `table_name`.

        :param table_name: The table
        :return: Sequence of `ColumnData` for every column in the table.
        """
        assert table_name in self.table_names
        query = f"PRAGMA table_info({table_name})"
        return [ColumnData(table_name, utilities.sql_type_to_enum_type(tpe), name, primary_key == 1)
                for _, name, tpe, _, _, primary_key in utilities.execute_query(query)]

    def get_data_from_table(self, table_name, columns_names: Iterable[str] = None) \
            -> Iterator[Iterable[str]]:
        """
        Retrieves the data in `table_name` for the given `columns_names`.
        The function would yield the columns names first, and then every row that applies to the given `filter`.

        :param table_name: The table from which data would be retrieved.
        :param columns_names: The name of the columns to retrieve, default is all the columns.
        :return: Yields the names of the columns and after that yields every row in the table.
        """
        assert table_name in self.table_names
        # If columns was not specified, select all the columns in the table
        if columns_names is None:
            columns_names = [col.get_full_name() for col in self.get_columns_for(table_name)]

        self.last_data_retrieve_query = query = f"SELECT {','.join(columns_names)} FROM {table_name}"

        yield from utilities.execute_query(query)

    def get_related_tables(self, main_table_name: str) -> Sequence[RelatedTable]:
        """
        Finds all the tables that are related to `main_table_name` based on the foreign keys.

        :param main_table_name: The table to which we search related tables.
        :return: Sequence of `RelatedTable` instances for every table related to the given table.
        """
        assert main_table_name in self.table_names
        # Source: https://stackoverflow.com/a/54422806
        query = f"PRAGMA foreign_key_list({main_table_name})"
        return [RelatedTable(table_name, from_, to)
                for _, _, table_name, from_, to, *_ in utilities.execute_query(query)
                if table_name != main_table_name]

    def join_tables(self, main_table: str, *related_tables: RelatedTable) \
            -> Tuple[Iterable[ColumnData], Iterable[str]]:
        """
        Retrieves all the data from `main_table` and the related tables.

        :param main_table: The table from which data would be retrieved.
        :param related_tables: The tables from which we would join the data.
        :return: Yields the columns names and then yields every row in the table
        """
        # Make sure the table is in the database.
        assert main_table in self.table_names

        # Get the info about the columns in the main table.
        table_columns_data = self.get_columns_for(main_table)

        # A list of the join queries for every table.
        join_queries: List[str] = []

        for related_table in related_tables:
            related_table_name = related_table.table_name
            # Get the info about the columns in the related table and append them to the columns list.
            related_table_columns = self.get_columns_for(related_table.table_name)
            related_table_columns_data = [column for column in related_table_columns  # For every column in the table
                                           if column.title != related_table.to_column]  # Except the foreign-key

            # Add the JOIN query for the table.
            join_queries.append(f"""
                    JOIN {related_table.table_name}
                    ON {main_table}.{related_table.from_column} = {related_table_name}.{related_table.to_column}
                    """)
            # Add the table's columns to the columns list.
            table_columns_data += related_table_columns_data

        # And finally create the query.
        self.last_data_retrieve_query = final_query = f"""
                SELECT {','.join((column.get_full_name() for column in table_columns_data))}
                FROM {main_table}
                {' '.join(join_queries)}
            """
        return table_columns_data, utilities.execute_query(final_query)

    def filter_last_executed_query(self, filters: Iterable[Filter], case_sensitive: bool = False):
        assert len(self.last_data_retrieve_query) > 0
        query = utilities.add_filters_to_query(self.last_data_retrieve_query, filters, case_sensitive)
        yield from utilities.execute_queries((f'PRAGMA case_sensitive_like = {case_sensitive}', query))
