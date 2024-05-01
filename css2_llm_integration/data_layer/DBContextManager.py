import os

import psycopg

from css2_llm_integration.automation.experiment_config import ConfigReviewEntry


class ContextManager:
    db_conn: psycopg.AsyncConnection

    def __init__(self, db_conn: psycopg.AsyncConnection):
        self._db_conn = db_conn

    async def rebuild_db(self):
        schema_path = f"{os.getenv('PROJECT_ROOT')}/database_schema"
        async with self._db_conn.cursor() as cursor:
            schemas = sorted(os.listdir(schema_path))
            for schema in schemas:
                if schema.startswith("99"):
                    continue

                with open(f"{schema_path}/{schema}", "r") as f:
                    await cursor.execute(str(f.read()))
                    await cursor.connection.commit()
        await self.insert_data()

    async def insert_data(self):
        data_folder = os.getenv("DB_DATA_FOLDER")
        async with self._db_conn.cursor() as cursor:
            data = sorted(os.listdir(data_folder))
            for entry in data:
                table = entry.split("-")[1].rstrip(".csv")
                await cursor.execute(
                    f"COPY {table} FROM \'{data_folder}/{entry}\' "
                    f"WITH (FORMAT csv, DELIMITER ',', "
                    f"HEADER MATCH, DEFAULT '<>');")
                await cursor.connection.commit()

    async def add_review(self, review: ConfigReviewEntry):
        async with self._db_conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO product_review (product_id, name, review, rating) VALUES (%s, %s, %s, %s)", (
                    review.product_id,
                    review.name,
                    review.review,
                    review.score
                ))
            await cursor.connection.commit()