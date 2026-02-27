from sqlalchemy import create_engine, text

DB_USER = "finance"
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "company_finance"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def execute_sql(sql_query):
    """Выполняет SQL и возвращает результат в виде списка словарей"""
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        return [dict(row) for row in result]