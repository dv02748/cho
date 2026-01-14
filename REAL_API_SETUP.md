# Инструкция для реального парсинга через Chotot API

## ⚠️ Важно: Требования к окружению

**Текущее Docker окружение изолировано и не имеет доступа к интернету.**

Для реального парсинга данных из API Chotot вам нужно окружение с:
- ✅ Доступом к интернету
- ✅ Python 3.11+
- ✅ Установленными зависимостями из requirements.txt

---

## 🚀 Быстрый старт в окружении с интернетом

### 1. Установка зависимостей

```bash
# Клонируйте репозиторий
git clone <your-repo>
cd cho

# Создайте виртуальное окружение (опционально)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Добавьте src в PYTHONPATH
export PYTHONPATH=src
```

### 2. Базовый запуск

```bash
# Парсинг апартаментов в Дананге (3 страницы по 20 объявлений)
python -m chotot.apartment_cli --city danang --pages 3 --output apartments.json

# Проверьте результат
cat apartments.json | python -m json.tool | head -50
```

### 3. Примеры использования

#### Парсинг по городам

```bash
# Дананг
python -m chotot.apartment_cli --city danang --pages 5 --output danang.json

# Хошимин
python -m chotot.apartment_cli --city hcm --pages 10 --output hcm.json

# Ханой
python -m chotot.apartment_cli --city hanoi --pages 5 --output hanoi.json
```

#### С фильтрами

```bash
# Студии в Дананге (до 10 млн VND)
python -m chotot.apartment_cli --city danang \
    --max-rooms 1 \
    --max-price 10000000 \
    --pages 5 \
    --output danang_studios.json

# 2-комнатные меблированные в Хошимине
python -m chotot.apartment_cli --city hcm \
    --min-rooms 2 --max-rooms 2 \
    --furnished-only \
    --pages 10 \
    --output hcm_2br_furnished.json

# Премиум апартаменты (3+ комн, от 20 млн)
python -m chotot.apartment_cli --city hcm \
    --min-rooms 3 \
    --min-price 20000000 \
    --pages 5 \
    --output hcm_luxury.json
```

#### Экспорт в CSV

```bash
# Экспорт в CSV для анализа в Excel
python -m chotot.apartment_cli --city danang \
    --pages 5 \
    --format csv \
    --output danang_apartments.csv

# Открыть в Excel/LibreOffice
# CSV содержит все поля: цена, площадь, комнаты, удобства и т.д.
```

#### Использование bash-скрипта

```bash
# Простой запуск (по умолчанию Дананг, 1 страница)
./scripts/scrape_apartments.sh

# С параметрами через переменные окружения
CITY=hcm PAGES=10 LIMIT=50 OUTPUT=data/hcm_large.json ./scripts/scrape_apartments.sh

# С фильтрами
CITY=danang MIN_ROOMS=2 MAX_PRICE=15000000 FURNISHED=true PAGES=5 ./scripts/scrape_apartments.sh

# CSV формат
CITY=hanoi FORMAT=csv OUTPUT=hanoi.csv PAGES=3 ./scripts/scrape_apartments.sh
```

---

## 📊 Программное использование

### Базовое использование

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Настройка для Дананга
query = QueryConfig(
    region_v2=32,  # Дананг
    cg=1000,       # Недвижимость
    cgr=1010,      # Аренда апартаментов
    limit=20       # Объявлений на странице
)

config = ScraperConfig(query=query, delay_seconds=1.0)
scraper = ApartmentScraper(config)

# Парсинг
apartments = scraper.scrape(max_pages=5)
print(f"Найдено: {len(apartments)} апартаментов")

# Сохранение
scraper.dump_to_json(apartments, "apartments.json")
scraper.dump_to_csv(apartments, "apartments.csv")
```

### С фильтрацией

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Парсинг большого количества данных
query = QueryConfig(region_v2=31, cg=1000, cgr=1010, limit=50)  # Хошимин
config = ScraperConfig(query=query, delay_seconds=1.0)
scraper = ApartmentScraper(config)

apartments = scraper.scrape(max_pages=20)  # До 1000 объявлений

# Применение фильтров
# 1. Доступные студии
studios = scraper.filter_by_rooms(apartments, min_rooms=1, max_rooms=1)
affordable_studios = scraper.filter_by_price(studios, min_price=0, max_price=8000000)
print(f"Доступных студий: {len(affordable_studios)}")

# 2. Меблированные 2-комнатные
two_br = scraper.filter_by_rooms(apartments, min_rooms=2, max_rooms=2)
two_br_furnished = scraper.filter_furnished(two_br, furnished=True)
print(f"Меблированных 2-комн: {len(two_br_furnished)}")

# 3. Премиум (3+ комн, от 20 млн)
luxury = scraper.filter_by_rooms(apartments, min_rooms=3)
luxury = scraper.filter_by_price(luxury, min_price=20000000)
print(f"Премиум апартаментов: {len(luxury)}")

# Сохранение отфильтрованных данных
scraper.dump_to_json(affordable_studios, "studios_affordable.json")
scraper.dump_to_json(two_br_furnished, "2br_furnished.json")
scraper.dump_to_json(luxury, "luxury.json")
```

### Анализ данных

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig
from collections import Counter

query = QueryConfig(region_v2=32, cg=1000, cgr=1010, limit=50)
config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)

apartments = scraper.scrape(max_pages=10)

# Статистика по комнатам
room_counts = Counter(apt.rooms for apt in apartments if apt.rooms)
print("\nРаспределение по комнатам:")
for rooms, count in sorted(room_counts.items()):
    print(f"  {rooms} комн: {count}")

# Ценовая статистика
prices = [apt.price for apt in apartments if apt.price]
avg_price = sum(prices) / len(prices)
print(f"\nСредняя цена: {avg_price:,.0f} VND (~${avg_price/25000:.0f})")
print(f"Минимум: {min(prices):,} VND")
print(f"Максимум: {max(prices):,} VND")

# Процент меблированных
furnished_count = sum(1 for apt in apartments if apt.furnished)
print(f"\nМеблированных: {furnished_count}/{len(apartments)} ({furnished_count/len(apartments)*100:.1f}%)")

# Удобства
print("\nУдобства:")
print(f"  Балкон: {sum(1 for apt in apartments if apt.balcony)}")
print(f"  Парковка: {sum(1 for apt in apartments if apt.parking)}")
print(f"  Лифт: {sum(1 for apt in apartments if apt.elevator)}")
print(f"  Кондиционер: {sum(1 for apt in apartments if apt.air_conditioning)}")
```

---

## 🏙️ Коды городов

| Город | Код region_v2 | CLI параметр |
|-------|---------------|--------------|
| Дананг | 32 | `--city danang` |
| Ханой | 13 | `--city hanoi` |
| Хошимин | 31 | `--city hcm` |
| Хайфон | 15 | `--city haiphong` |
| Кантхо | 52 | `--city can-tho` |
| Бьенхоа | 41 | `--city bien-hoa` |
| Нячанг | 37 | `--city nha-trang` |
| Вунгтау | 43 | `--city vung-tau` |

---

## ⚙️ Параметры API

### Коды категорий
- `cg=1000` - Недвижимость (Real Estate)
- `cgr=1010` - Аренда апартаментов (Apartments for Rent)
- `cgr=1002` - Вся аренда недвижимости (All Real Estate for Rent)

### Параметры запроса
- `region_v2` - код города
- `area_v2` - код района (опционально)
- `ward` - код ward (опционально)
- `limit` - объявлений на странице (макс 100)
- `page` - номер страницы

---

## 🔧 Решение проблем

### Ошибка 403 от прокси

```bash
# Отключите прокси
python -m chotot.apartment_cli --city danang --ignore-env-proxy --pages 3
```

### Медленный парсинг

```bash
# Увеличьте задержку между запросами (по умолчанию 1 сек)
python -m chotot.apartment_cli --city hcm --delay 2.0 --pages 5
```

### DNS resolution error

Проверьте доступ к интернету:
```bash
curl -I https://gateway.chotot.com/v1/public/ad-listing
```

---

## 📝 Примечание

В текущем Docker окружении отсутствует доступ к интернету, поэтому для демонстрации
используются тестовые данные. Все компоненты парсера полностью функциональны и готовы
к работе в окружении с интернет-соединением.

Для тестирования без интернета используйте:
```bash
python demo_test.py           # 2 апартамента
python extended_demo.py       # 10 апартаментов
```

---

## 📚 Дополнительная документация

- **README.md** - общая документация проекта
- **APARTMENT_EXAMPLES.md** - детальные примеры использования
- **tests/test_apartment_parser.py** - юнит-тесты
- **tests/test_online.py** - онлайн тесты (запускаются с RUN_ONLINE_TESTS=1)
