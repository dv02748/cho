# ChoTot scraping service

Универсальный сервис для сбора объявлений с chotot.com с готовой конфигурацией под аренду недвижимости в Дана́нге и возможностью масштабирования на другие города и категории.

## Возможности
- Запрос данных через публичный API (`gateway.chotot.com/v1/public/ad-listing`).
- Гибкая конфигурация параметров (город `region_v2`, район `area_v2`, категория `cg/cgr`, лимиты, задержки).
- Поддержка пагинации, логирования и экспорта в JSON/CSV.
- REST API на FastAPI: получение объявлений и выгрузка.
- CLI-утилита для офлайн-выгрузки.
- **Специализированный парсер для аренды апартаментов** с расширенными полями (количество комнат, мебель, этаж, балкон и т.д.).
- Встроенная фильтрация по количеству комнат, цене, наличию мебели.
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
- `chotot.apartment_models` — расширенная модель `ApartmentListing` с дополнительными полями.
- `chotot.apartment_parser` — парсер для апартаментов с извлечением специфичных полей.
- `chotot.apartment_service` — сервис для парсинга апартаментов с фильтрацией.
- `chotot.apartment_cli` — CLI для удобного поиска апартаментов в разных городах.

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

## Парсер апартаментов

Специализированный парсер для аренды апартаментов с расширенными полями и встроенной фильтрацией.

### Дополнительные поля для апартаментов
- `rooms` — количество спален
- `bathrooms` — количество ванных комнат
- `floor` — этаж
- `furnished` — наличие мебели (true/false)
- `furniture_type` — тип меблировки ("full", "partial", "none")
- `building_name` — название здания/комплекса
- `balcony` — наличие балкона
- `parking` — наличие парковки
- `elevator` — наличие лифта
- `pets_allowed` — разрешены ли питомцы
- `air_conditioning` — наличие кондиционера
- `direction` — ориентация (Север, Юг и т.д.)
- `apartment_type` — тип апартаментов ("studio", "duplex", "penthouse")

### Использование CLI для апартаментов

```bash
# Установите зависимости
export PYTHONPATH=src

# Поиск апартаментов в Дананге
python -m chotot.apartment_cli --city danang --pages 3 --output apartments.json

# Поиск апартаментов в Хошимине с фильтрами
python -m chotot.apartment_cli --city hcm --min-rooms 2 --max-price 15000000 --pages 5

# Только меблированные апартаменты
python -m chotot.apartment_cli --city hanoi --furnished-only --format csv --output hanoi_furnished.csv

# Фильтрация по количеству комнат
python -m chotot.apartment_cli --city danang --min-rooms 1 --max-rooms 2 --pages 3

# Использование bash-скрипта
./scripts/scrape_apartments.sh

# Скрипт с параметрами через переменные окружения
CITY=hcm PAGES=5 MIN_ROOMS=2 MAX_PRICE=20000000 ./scripts/scrape_apartments.sh

# Экспорт в CSV
CITY=danang FORMAT=csv OUTPUT=data/danang_apartments.csv ./scripts/scrape_apartments.sh
```

### Доступные города

CLI поддерживает следующие предустановленные коды городов:
- `danang` / `da-nang` — Дананг (region_v2=32)
- `hanoi` — Ханой (region_v2=13)
- `hcm` / `ho-chi-minh` / `saigon` — Хошимин (region_v2=31)
- `haiphong` — Хайфон (region_v2=15)
- `can-tho` — Кантхо (region_v2=52)
- `bien-hoa` — Бьенхоа (region_v2=41)
- `nha-trang` — Нячанг (region_v2=37)
- `vung-tau` — Вунгтау (region_v2=43)

### Примеры использования

```bash
# Студии в Дананге
python -m chotot.apartment_cli --city danang --max-rooms 1 --pages 2

# Апартаменты с 2+ спальнями в Хошимине, до 20 млн донгов
python -m chotot.apartment_cli --city hcm --min-rooms 2 --max-price 20000000 --pages 5

# Только меблированные апартаменты в Ханое, экспорт в CSV
python -m chotot.apartment_cli --city hanoi --furnished-only --format csv --output hanoi_apartments.csv

# Использование пользовательского кода региона
python -m chotot.apartment_cli --region 32 --pages 3 --output custom_region.json
```

### Программное использование

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Настройка для поиска апартаментов в Дананге
query = QueryConfig(
    region_v2=32,  # Дананг
    cg=1000,       # Недвижимость
    cgr=1010,      # Аренда апартаментов
    limit=20
)

config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)

# Сбор данных
apartments = scraper.scrape(max_pages=3)

# Фильтрация
apartments_2br = scraper.filter_by_rooms(apartments, min_rooms=2, max_rooms=2)
affordable = scraper.filter_by_price(apartments, min_price=0, max_price=10000000)
furnished = scraper.filter_furnished(apartments, furnished=True)

# Экспорт
scraper.dump_to_json(apartments, "apartments.json")
scraper.dump_to_csv(apartments, "apartments.csv")
```
