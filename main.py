from agent.rag_loader import load_rag_examples
from agent.prompt import build_prompt
from agent.sql_exec import execute_sql
import requests
import os
print(os.getenv("HF_API_TOKEN"))
# --- Настройки Hugging Face API ---
#HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # сохраните токен в переменную окружения
API_URL ="https://router.huggingface.co/hf-inference/models/google/flan-t5-base"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_hf(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.0
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("HF error:", response.status_code, response.text)
        raise RuntimeError("Ошибка запроса к Hugging Face API")

    data = response.json()
    return data[0]["generated_text"]

# --- Загружаем RAG-примеры ---
rag_examples = load_rag_examples(path="data/rag_examples.json")

# --- Краткая схема базы для prompt ---
schema_info = """
orders(order_id, order_date, order_status, customer_id, customer_name, city, state, country, payment_method, tax, shipping_cost, total_amount)
order_items(order_id, seller_id, product_id, product_name, category, brand, quantity, unit_price, discount)
"""

def ask_question(user_question):
    # Строим prompt с RAG-примерами
    prompt = build_prompt(user_question, rag_examples, schema_info)
    
    # Генерация SQL через Hugging Face API
    sql_query = query_hf(prompt).strip()
    
    # Выполняем SQL
    result = execute_sql(sql_query)
    
    return {"query": sql_query, "result": result}

if __name__ == "__main__":
    print("Text2SQL агент через Hugging Face API готов!")
    question = input("Задайте вопрос: ")
    output = ask_question(question)
    
    print("\nСгенерированный SQL:\n", output["query"])
    print("\nРезультат:\n", output["result"])