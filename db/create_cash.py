import psycopg2
from psycopg2 import sql


def create_cache_table(db_params: dict):
    """
    Создаёт таблицу sql_cache, если она ещё не существует
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sql_cache (
        id              SERIAL PRIMARY KEY,
        question_hash   TEXT UNIQUE NOT NULL,
        original_question TEXT NOT NULL,
        sql_query       TEXT NOT NULL,
        embedding       BYTEA,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hits            INTEGER DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_sql_cache_hash 
        ON sql_cache(question_hash);
    
    CREATE INDEX IF NOT EXISTS idx_sql_cache_created_at 
        ON sql_cache(created_at);
    """

    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_query)
                conn.commit()
        print("Таблица sql_cache успешно создана (или уже существует)")
    except Exception as e:
        print(f"Ошибка при создании таблицы sql_cache: {e}")


if __name__ == "__main__":
    db_params = {
        "dbname": "company_finance",
        "user": "finance",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "5432"
    }
    
    create_cache_table(db_params)