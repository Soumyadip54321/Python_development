'''
Script that demonstrates testing backend API server functionalities.
Both context manager (i.e. get_db_cursor) & mysql.connector.connect is mocked.
'''
from ExpenseTracker.backend import db_interaction
import pytest
from unittest.mock import patch, MagicMock


class TestDBInteraction:

    @staticmethod
    def mock_connect():
        '''
        Mocks mysql database connection.
        :return:
        '''
        # ====== Mock 1: MYSQL connection ============
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor._connection = mock_conn  # For database commits.

        return mock_conn

    @staticmethod
    def mock_context(connection_with_custom_cursor_fetchall_result):
        '''
        Mocks context manager get_db_cursor.
        :param self:
        :param connection_with_custom_cursor_fetchall_result: Connection that returns custom result on executing 'fetchall' on cursor.
        :return:
        '''
        # ====== Mock 2: Context Manager i.e. get_db_cursor with custom cursor.fetchall result========
        mock_context = MagicMock()
        mock_context.__enter__.return_value = connection_with_custom_cursor_fetchall_result.mock_cursor
        mock_context.__exit__.return_value = None

        return mock_context

    @patch('Projects.ExpenseTracker.backend.db_interaction.get_db_cursor')
    @patch('Projects.ExpenseTracker.backend.db_interaction.mysql.connector.connect')
    def test_fetch_all_records(self,mock_connection,mock_get_db_cursor):
        '''
        Function to test expenses between dates
        :param mock_conn: Mocks mysql database connection.
        :param mock_get_db_cursor: Mocks context manager
        :return:
        '''

        # Mock Database Connection
        mock_connection.return_value = self.mock_connect
        mock_connection.mock_cursor.fetchall.return_value = [{'id': '3', 'date': '2024-08-02', 'amount': '50', 'category': 'Entertainment', 'description': 'Movie tickets'}]

        # Mock Context Manager
        mock_get_db_cursor.return_value = self.mock_context(mock_connection)

        # ======== test result ================
        result = db_interaction.fetch_all_records()
        assert len(result) == 1
        assert result[0] == {'id': '3', 'date': '2024-08-02', 'amount': '50', 'category': 'Entertainment', 'description': 'Movie tickets'},"Fetch Failed"

if __name__ == '__main__':
    obj = TestDBInteraction()
    obj.test_fetch_all_records()