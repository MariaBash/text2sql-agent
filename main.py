from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import re
from g4f import ChatCompletion
from agent.rag_loader import RAGLoader
from agent.prompt import PromptGenerator
from agent.sql_exec import SQLValidatorExecutor
from agent.cache_manager import CacheManager

def call_llm(prompt: str) -> str:
    import g4f
    
    try:
        resp = g4f.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "Ты эксперт по PostgreSQL. Отвечай ТОЛЬКО SQL-запросом внутри блока ```sql ... ```. Никаких объяснений, комментариев и лишнего текста."},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp
    except Exception as e:
        return f"LLM failed: {str(e)}"

rag = RAGLoader()
prompt_gen = PromptGenerator(rag)
db_params = { 
       "dbname":   "company_finance",
        "user":     "finance",
        "password": "mysecretpassword",              
        "host":     "localhost",
        "port":     "5432"
}
sql_exec = SQLValidatorExecutor(db_params)

app = FastAPI(title="Text2SQL Agent")

class QueryRequest(BaseModel):
    question: str

cache = CacheManager(db_params) 

@app.post("/query")
async def query(request: QueryRequest):
    cached_sql = cache.get_cached_sql(request.question)
    
    if cached_sql:
        result = sql_exec.execute(cached_sql)
        return {
            "question": request.question,
            "sql": cached_sql,
            "result": result.get("result", []),
            "error": result.get("error"),
            "from_cache": True
        }

    prompt = prompt_gen.generate(request.question)
    llm_response = call_llm(prompt)
    
    match = re.search(r"```sql\s*(.*?)\s*```", llm_response, re.DOTALL | re.IGNORECASE)
    sql = match.group(1).strip() if match else llm_response.strip()
    
    result = sql_exec.execute(sql)
    if not result.get("error"):
        cache.save_to_cache(request.question, sql)

    return {
        "question": request.question,
        "sql": sql,
        "result": result.get("result", []),
        "error": result.get("error"),
        "from_cache": False
    }
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)