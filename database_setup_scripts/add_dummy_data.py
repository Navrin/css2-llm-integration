import dotenv
import psycopg2
import os
import csv
def main():
    dotenv.load_dotenv("../.env")
    cfg = dotenv.dotenv_values()

    db = psycopg2.connect(f"dbname={cfg['DB_NAME']}")
    tables = os.listdir("../example_data")
    sorted_tables = sorted(tables, key=lambda x: int(x.split("-")[0]))
    with db.cursor() as cur:
        for table in sorted_tables:
            table_name = table.split(".")[0].split("-")[1]
            table_sql = ""
            with open(f"../example_data/{table}") as csv_file:
                entries = csv.DictReader(csv_file)
                names = ",".join(list(entries.fieldnames))
                for entry in entries:
                    items = list(map(lambda x:  f"$${x}$$", entry.values()))
                    print(items)
                    table_sql += f"INSERT INTO {table_name} ({names}) VALUES ({','.join(items)});"
            cur.execute(table_sql)
    db.commit()


if __name__ == "__main__":
    main()