# ChoTot scraping service

Универсальный сервис для сбора объявлений с chotot.com с готовой конфигурацией под аренду недвижимости в Дана́нге и возможностью масштабирования на другие города и категории.

## Возможности
- Запрос данных через публичный API (`gateway.chotot.com/v1/public/ad-listing`).
- Гибкая конфигурация параметров (город `region_v2`, район `area_v2`, категория `cg/cgr`, лимиты, задержки).
- Поддержка пагинации, логирования и экспорта в JSON/CSV.
- REST API на FastAPI: получение объявлений и выгрузка.
- CLI-утилита для офлайн-выгрузки.
- Юнит-тесты и интеграционный тест (отключен по умолчанию).

## Быстрый старт
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите API:
   ```bash
   uvicorn chotot.api:app --reload
   ```
   Пример запроса для аренды в Дана́нге (параметры кодов нужно уточнить через Network в браузере):
   ```bash
   curl "http://localhost:8000/listings?region_v2=32&cg=1000&cgr=1002&pages=1&limit=10"
   ```
3. CLI для выгрузки в файл:
   ```bash
   python -m chotot.cli --region 32 --cg 1000 --cgr 1002 --pages 2 --limit 20 --output danang.json
   ```

> **Примечание о кодах региона/категории.** Chotot использует числовые идентификаторы. Узнать их можно в вкладке Network браузера при фильтрации на сайте. Для аренды недвижимости используются `cg=1000` (Real Estate) и `cgr=1002` (For Rent). Код региона для Дана́нга часто обозначается как `region_v2=32`, но при необходимости его можно изменить через параметры.

## Локальная разработка без Docker
Если хотите запускать API и парсер прямо на хосте, используйте готовые CLI-команды:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Добавьте исходники в PYTHONPATH (нужно для uvicorn/python -m)
export PYTHONPATH=src

# Запуск REST API с автоперезапуском
uvicorn chotot.api:app --reload

# В другом терминале запросите данные у запущенного API
curl "http://localhost:8000/listings?region_v2=32&cg=1000&cgr=1002&pages=1&limit=5" | python -m json.tool

# CLI для выгрузки напрямую (минуя сервер)
python -m chotot.cli --region 32 --cg 1000 --cgr 1002 --pages 2 --limit 20 --output listings.json

# Сохранить сразу в CSV
python -m chotot.cli --region 32 --cg 1000 --cgr 1002 --pages 2 --limit 20 --format csv --output listings.csv

# Если корпоративный прокси возвращает 403, отключите переменные HTTP(S)_PROXY
python -m chotot.cli --region 32 --cg 1000 --cgr 1002 --pages 1 --limit 10 --ignore-env-proxy --output listings.json

# Быстрый скрипт для CLI (создает data/listings.json по умолчанию)
./scripts/run_cli.sh
PAGES=3 LIMIT=50 OUTPUT=data/run.json ./scripts/run_cli.sh
FORMAT=csv ./scripts/run_cli.sh
```

## Архитектура
- `chotot.config` — конфигурация запросов и глобальные настройки.
- `chotot.client` — HTTP-клиент с retries, user-agent spoofing и задержками.
- `chotot.parser` — нормализация JSON → модель `Listing`.
- `chotot.service` — управление пагинацией, агрегация, экспорт.
- `chotot.api` — FastAPI-приложение (`/health`, `/listings`, `/listings/export`).
- `chotot.cli` — командный интерфейс.

## Тесты
- Офлайн тесты (по фикстурам):
  ```bash
  pytest -q
  ```
- Онлайн тест (включается переменной `RUN_ONLINE_TESTS=1`):
  ```bash
  RUN_ONLINE_TESTS=1 pytest tests/test_online.py -q
  ```
  Тест пропустится, если сеть/параметры недоступны.

## Запуск через Docker Compose
1. Соберите и поднимите сервис:
   ```bash
   docker compose up -d --build
   ```
2. Проверьте healthcheck:
   ```bash
   curl http://localhost:8000/health
   ```
3. Запросите живые объявления через API (пример для аренды в Дана́нге):
   ```bash
   curl "http://localhost:8000/listings?region_v2=32&cg=1000&cgr=1002&pages=1&limit=3" | python -m json.tool
   ```

4. Когда закончите, остановите и удалите контейнеры:
   ```bash
   docker compose down --remove-orphans
   ```

> Для быстрой проверки можно воспользоваться скриптом `scripts/compose_smoke.sh`, который поднимает контейнер и делает реальный запрос.
