# Примеры использования парсера апартаментов

Этот документ содержит практические примеры использования специализированного парсера для аренды апартаментов на Chotot.

## Быстрый старт

### 1. Простой поиск апартаментов в городе

```bash
# Дананг
python -m chotot.apartment_cli --city danang --pages 3 --output data/danang_apartments.json

# Хошимин
python -m chotot.apartment_cli --city hcm --pages 5 --output data/hcm_apartments.json

# Ханой
python -m chotot.apartment_cli --city hanoi --pages 2 --output data/hanoi_apartments.json
```

### 2. Поиск с фильтрацией

```bash
# Студии в Дананге (0-1 комната)
python -m chotot.apartment_cli --city danang --max-rooms 1 --pages 3

# 2-комнатные апартаменты в Хошимине
python -m chotot.apartment_cli --city hcm --min-rooms 2 --max-rooms 2 --pages 5

# Апартаменты с 2+ спальнями, до 15 млн донгов
python -m chotot.apartment_cli --city danang --min-rooms 2 --max-price 15000000 --pages 3

# Дорогие апартаменты (от 20 млн донгов)
python -m chotot.apartment_cli --city hcm --min-price 20000000 --pages 5
```

### 3. Фильтрация по мебели

```bash
# Только меблированные апартаменты
python -m chotot.apartment_cli --city danang --furnished-only --pages 3

# Меблированные студии
python -m chotot.apartment_cli --city hanoi --furnished-only --max-rooms 1 --pages 2
```

### 4. Экспорт в CSV

```bash
# Сохранить результаты в CSV
python -m chotot.apartment_cli --city danang --format csv --output data/danang.csv

# Меблированные апартаменты в CSV
python -m chotot.apartment_cli --city hcm --furnished-only --format csv --output data/hcm_furnished.csv
```

### 5. Использование bash-скрипта

```bash
# Простой запуск (использует настройки по умолчанию)
./scripts/scrape_apartments.sh

# С параметрами через переменные окружения
CITY=hcm PAGES=5 ./scripts/scrape_apartments.sh

# Фильтрация через переменные
CITY=danang MIN_ROOMS=2 MAX_PRICE=15000000 PAGES=3 ./scripts/scrape_apartments.sh

# Только меблированные
CITY=hanoi FURNISHED=true PAGES=5 FORMAT=csv ./scripts/scrape_apartments.sh

# Комбинация фильтров
CITY=hcm MIN_ROOMS=2 MAX_ROOMS=3 MIN_PRICE=10000000 MAX_PRICE=25000000 FURNISHED=true PAGES=10 OUTPUT=data/premium_apartments.json ./scripts/scrape_apartments.sh
```

## Программное использование

### Базовое использование

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Настройка для Дананга
query = QueryConfig(
    region_v2=32,  # Дананг
    cg=1000,       # Недвижимость
    cgr=1010,      # Аренда апартаментов
    limit=20
)

config = ScraperConfig(query=query, delay_seconds=1.0)
scraper = ApartmentScraper(config)

# Получение данных
apartments = scraper.scrape(max_pages=3)
print(f"Найдено {len(apartments)} апартаментов")

# Сохранение в файл
scraper.dump_to_json(apartments, "data/apartments.json")
```

### Фильтрация результатов

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Настройка
query = QueryConfig(region_v2=31, cg=1000, cgr=1010, limit=20)  # Хошимин
config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)

# Получение данных
apartments = scraper.scrape(max_pages=5)

# Фильтрация по количеству комнат
apartments_2br = scraper.filter_by_rooms(apartments, min_rooms=2, max_rooms=2)
print(f"2-комнатных: {len(apartments_2br)}")

# Фильтрация по цене
affordable = scraper.filter_by_price(apartments, min_price=0, max_price=15000000)
print(f"До 15 млн: {len(affordable)}")

# Только меблированные
furnished = scraper.filter_furnished(apartments, furnished=True)
print(f"Меблированных: {len(furnished)}")

# Комбинация фильтров
ideal = scraper.filter_by_rooms(apartments, min_rooms=2, max_rooms=2)
ideal = scraper.filter_by_price(ideal, max_price=15000000)
ideal = scraper.filter_furnished(ideal, furnished=True)
print(f"Идеальных вариантов: {len(ideal)}")

# Сохранение отфильтрованных результатов
scraper.dump_to_json(ideal, "data/ideal_apartments.json")
scraper.dump_to_csv(ideal, "data/ideal_apartments.csv")
```

### Работа с данными апартаментов

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

# Настройка и получение данных
query = QueryConfig(region_v2=32, cg=1000, cgr=1010, limit=20)
config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)
apartments = scraper.scrape(max_pages=3)

# Анализ данных
for apt in apartments[:5]:  # Первые 5 апартаментов
    print(f"\n{apt.title}")
    print(f"  Цена: {apt.price:,} VND" if apt.price else "  Цена: не указана")
    print(f"  Площадь: {apt.area_m2} м²" if apt.area_m2 else "  Площадь: не указана")
    print(f"  Комнат: {apt.rooms}" if apt.rooms else "  Комнат: не указано")
    print(f"  Этаж: {apt.floor}" if apt.floor else "  Этаж: не указан")
    print(f"  Меблирована: {'Да' if apt.furnished else 'Нет'}")
    print(f"  Балкон: {'Да' if apt.balcony else 'Нет' if apt.balcony is not None else 'Не указано'}")
    print(f"  Парковка: {'Да' if apt.parking else 'Нет' if apt.parking is not None else 'Не указано'}")
    print(f"  Адрес: {apt.address}")
    print(f"  Контакт: {apt.contact_name} - {apt.phone}" if apt.contact_name else "")
```

### Статистика и анализ

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig
from collections import Counter

query = QueryConfig(region_v2=32, cg=1000, cgr=1010, limit=20)
config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)
apartments = scraper.scrape(max_pages=5)

# Статистика по количеству комнат
room_counts = Counter(apt.rooms for apt in apartments if apt.rooms)
print("\nРаспределение по количеству комнат:")
for rooms, count in sorted(room_counts.items()):
    print(f"  {rooms} комнат(а): {count} апартаментов")

# Средняя цена
prices = [apt.price for apt in apartments if apt.price]
if prices:
    avg_price = sum(prices) / len(prices)
    print(f"\nСредняя цена: {avg_price:,.0f} VND")
    print(f"Минимальная цена: {min(prices):,} VND")
    print(f"Максимальная цена: {max(prices):,} VND")

# Процент меблированных
furnished_count = sum(1 for apt in apartments if apt.furnished)
total = len(apartments)
print(f"\nМеблированных: {furnished_count}/{total} ({furnished_count/total*100:.1f}%)")

# Статистика по удобствам
balcony_count = sum(1 for apt in apartments if apt.balcony)
parking_count = sum(1 for apt in apartments if apt.parking)
elevator_count = sum(1 for apt in apartments if apt.elevator)
ac_count = sum(1 for apt in apartments if apt.air_conditioning)

print(f"\nУдобства:")
print(f"  С балконом: {balcony_count}")
print(f"  С парковкой: {parking_count}")
print(f"  С лифтом: {elevator_count}")
print(f"  С кондиционером: {ac_count}")
```

## Кастомные фильтры

```python
from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig

query = QueryConfig(region_v2=32, cg=1000, cgr=1010, limit=20)
config = ScraperConfig(query=query)
scraper = ApartmentScraper(config)
apartments = scraper.scrape(max_pages=5)

# Поиск апартаментов с балконом и парковкой
with_amenities = [apt for apt in apartments if apt.balcony and apt.parking]

# Поиск апартаментов на высоких этажах
high_floor = [apt for apt in apartments if apt.floor and apt.floor >= 5]

# Студии с мебелью до 10 млн
affordable_studios = [
    apt for apt in apartments
    if apt.rooms == 1 and apt.furnished and apt.price and apt.price <= 10000000
]

# Большие апартаменты (более 80 м²)
spacious = [apt for apt in apartments if apt.area_m2 and apt.area_m2 > 80]

print(f"С балконом и парковкой: {len(with_amenities)}")
print(f"На высоких этажах: {len(high_floor)}")
print(f"Доступные студии с мебелью: {len(affordable_studios)}")
print(f"Просторные апартаменты: {len(spacious)}")
```

## Коды городов

| Город | Код | Параметр CLI |
|-------|-----|--------------|
| Дананг | 32 | `--city danang` |
| Ханой | 13 | `--city hanoi` |
| Хошимин | 31 | `--city hcm` / `--city saigon` |
| Хайфон | 15 | `--city haiphong` |
| Кантхо | 52 | `--city can-tho` |
| Бьенхоа | 41 | `--city bien-hoa` |
| Нячанг | 37 | `--city nha-trang` |
| Вунгтау | 43 | `--city vung-tau` |

Для других городов используйте `--region <код>` вместо `--city`.
