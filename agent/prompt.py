def build_prompt(user_question, rag_examples, schema_info):
    """
    user_question: str - вопрос пользователя
    rag_examples: list[dict] - примеры из RAG
    schema_info: str - краткое описание таблиц
    """
    prompt = f"Таблицы в базе: {schema_info}\n"
    prompt += "Примеры логики запросов:\n"
    
    for ex in rag_examples:
        prompt += f"Вопрос: {ex['question']}\n"
        prompt += "Логика:\n"
        for step in ex['logic']:
            prompt += f"- {step}\n"
    
    prompt += f"\nСгенерируй SQL для вопроса: {user_question}\n"
    prompt += "Только SQL, без объяснений."
    return prompt