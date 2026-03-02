from agent.rag_loader import RAGLoader

class PromptGenerator:
    def __init__(self, rag: RAGLoader):
        self.rag = rag
        self.schema = """
-- Таблицы (адаптируй под свой датасет, если нужно):
-- orders (orderid, orderdate, orderstatus, customerid, customername, city, state, country, paymentmethod, tax, shippingcost, totalamount, sellerid )
-- order_items (orderid, productid, productname, category, brand, quantity, unitprice, discount)
"""

        self.template = """
Ты эксперт по PostgreSQL. Напиши ТОЛЬКО SQL-запрос (без объяснений, без markdown кроме блока sql).

Схема БД:
{schema}

Примеры (используй их стиль и структуру):
{examples}

Вопрос пользователя: "{question}"

Ответь строго в формате:
```sql
ТВОЙ_SQL_ЗАПРОС
"""

    def generate(self, question: str, k: int = 5) -> str:
        retrieved = self.rag.retrieve(question, k)
        examples_str = "\n\n".join(
        f"Вопрос: {ex['question']}\nSQL:\n{ex['sql']}" for ex in retrieved
        )
        return self.template.format(
            schema=self.schema,
            examples=examples_str,
            question=question
        )