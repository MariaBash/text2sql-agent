import psycopg2
import json
from datetime import date, datetime

class SQLValidatorExecutor:
    def __init__(self, db_params: dict):
        """
        db_params = {
            "dbname": "your_db",
            "user": "postgres",
            "password": "pass",
            "host": "localhost",
            "port": "5432"
        }
        """
        self.db_params = db_params

    def _serialize_row(self, row: tuple, columns: list) -> dict:
        """Приводим даты к строке для JSON"""
        result = {}
        for col, val in zip(columns, row):
            if isinstance(val, (date, datetime)):
                result[col] = val.isoformat()
            else:
                result[col] = val
        return result

    def execute(self, sql: str) -> dict:
        dangerous = {"DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "GRANT"}
        if any(word in sql.upper() for word in dangerous):
            return {"error": "Запрещённая операция в SQL", "sql": sql}

        try:
            with psycopg2.connect(**self.db_params) as conn:
                conn.set_session(readonly=True) 
                with conn.cursor() as cur:
                    cur.execute(sql)
                    
                    if cur.description:  # SELECT
                        columns = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        result = [self._serialize_row(row, columns) for row in rows]
                    else:
                        result = [{"status": "OK (no result set)"}]
                    
                    return {"sql": sql, "result": result}
        except Exception as e:
            return {"error": str(e), "sql": sql}