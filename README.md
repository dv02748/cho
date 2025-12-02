# ChoTot scraping service

Парсер объявлений ChoTot для аренды недвижимости в Дананге с возможностью масштабирования на другие города/категории. Реализован API на FastAPI для получения сохранённых объявлений и запуска обновления.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn chotot_parser.api:app --host 0.0.0.0 --port 8000
```

Эндпойнты:
- `GET /health` — проверка статуса.
- `GET /listings` — отдаёт сохранённые объявления.
- `POST /listings/refresh` — запускает сбор объявлений (по умолчанию Дананг + аренда недвижимости).

## Конфигурация

Основные параметры находятся в `ScraperConfig`:
- `city` / `city_region_id` — город и его идентификатор.
- `category_id` — категория (1003 — аренда недвижимости).
- `limit`, `max_pages`, `delay_seconds` — параметры пагинации и задержек.

## Тесты

Онлайн-часть вынесена из тестов: модульные тесты используют `DummyClient` с заготовленными ответами.

```bash
pytest
```
