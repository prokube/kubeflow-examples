import logging
from typing import List

import psycopg2
from psycopg2 import DatabaseError

logger = logging.getLogger(__name__)


class PostgresClient:
    def __init__(
        self, database_user: str, password: str, database: str, host: str, port: int = 5432
    ):
        self.connection = psycopg2.connect(
            database=database, user=user, host=host, password=password, port=port
        )
        self.cursor = self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()

    def create_table(self, name: str, schema: str = "public"):
        try:
            self.cursor.execute(
                f"""CREATE TABLE {schema}.{name}(
                request_id SERIAL PRIMARY KEY,
                tsz timestamp with time zone NOT NULL,
                request json NOT NULL,
                response json NOT NULL);
                """
            )
        except DatabaseError as db:
            logger.error("Unable to create table: %s", db)

    def add_request(str t

    def execute(self, query: str):

        self.cursor.execute(query)
