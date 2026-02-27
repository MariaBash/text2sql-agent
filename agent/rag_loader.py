import json

def load_rag_examples(path="data/rag_examples.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Пример использования:
# rag_examples = load_rag_examples()