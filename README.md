Запустить приложение:
Сначала запустить докер
docker compose up -d
pip install -r requirements.txt
python db/load_dataset.py
python db/create_cash.py
uvicorn main:app --reload

