from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import re
from g4f import ChatCompletion
# Импортируем наши модули
from agent.rag_loader import RAGLoader
from agent.prompt import PromptGenerator
from agent.sql_exec import SQLValidatorExecutor

def call_llm(prompt: str) -> str:
    import g4f
    
    try:
        resp = g4f.ChatCompletion.create(
            model="gpt-4",  # ← сюда можно подставить любую рабочую модель
            messages=[
                {"role": "system", "content": "Ты эксперт по PostgreSQL. Отвечай ТОЛЬКО SQL-запросом внутри блока ```sql ... ```. Никаких объяснений, комментариев и лишнего текста."},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp
    except Exception as e:
        return f"LLM failed: {str(e)}"

# Инициализация (один раз при старте)
rag = RAGLoader()
prompt_gen = PromptGenerator(rag)
db_params = {  # ← подставь свои
       "dbname":   "company_finance",
        "user":     "finance",
        "password": "mysecretpassword",               # ← поменяй на реальный пароль
        "host":     "localhost",
        "port":     "5432"
}
sql_exec = SQLValidatorExecutor(db_params)

app = FastAPI(title="Text2SQL Agent Demo")

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(request: QueryRequest):
    # 1. Генерируем промт с RAG
    prompt = prompt_gen.generate(request.question)
    
    # 2. Просим LLM
    llm_response = call_llm(prompt)
    
    # 3. Извлекаем SQL
    match = re.search(r"```sql\s*(.*?)\s*```", llm_response, re.DOTALL | re.IGNORECASE)
    sql = match.group(1).strip() if match else llm_response.strip()
    
    # 4. Проверяем и выполняем
    result = sql_exec.execute(sql)
    
    # Возвращаем ровно то, что нужно на интервью
    return {
        "sql": result.get("sql"),
        "result": result.get("result", []),
        "error": result.get("error")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)