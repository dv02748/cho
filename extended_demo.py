#!/usr/bin/env python3
"""Extended demo with 10 apartments from different Vietnamese cities."""

import sys
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "src"))

from chotot.apartment_parser import parse_apartments
from chotot.apartment_service import ApartmentScraper
from chotot.config import ScraperConfig


def main():
    """Run extended demo with 10 apartments."""
    print("\n" + "="*70)
    print("РАСШИРЕННАЯ ДЕМОНСТРАЦИЯ: 10 АПАРТАМЕНТОВ ИЗ РАЗНЫХ ГОРОДОВ")
    print("="*70)

    fixture_path = Path(__file__).parent / "tests" / "tests_data" / "extended_apartment_ads.json"

    with open(fixture_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    config = ScraperConfig()
    apartments = parse_apartments(raw_data, config)
    scraper = ApartmentScraper(config)

    print(f"\n✅ Загружено: {len(apartments)} апартаментов")

    # City distribution
    print(f"\n{'='*70}")
    print("📍 РАСПРЕДЕЛЕНИЕ ПО ГОРОДАМ")
    print('='*70)
    city_counts = Counter(apt.city for apt in apartments)
    for city, count in city_counts.most_common():
        print(f"  {city}: {count} апартаментов")

    # Room distribution
    print(f"\n{'='*70}")
    print("🛏️ РАСПРЕДЕЛЕНИЕ ПО КОМНАТАМ")
    print('='*70)
    room_counts = Counter(apt.rooms for apt in apartments if apt.rooms)
    for rooms, count in sorted(room_counts.items()):
        if rooms == 1:
            room_type = "Студии/1-комнатные"
        else:
            room_type = f"{rooms}-комнатные"
        print(f"  {room_type}: {count} апартаментов")

    # Price ranges
    print(f"\n{'='*70}")
    print("💰 ЦЕНОВЫЕ ДИАПАЗОНЫ")
    print('='*70)
    prices = [apt.price for apt in apartments if apt.price]
    ranges = [
        (0, 5000000, "Бюджет (< 5 млн)"),
        (5000000, 10000000, "Средний (5-10 млн)"),
        (10000000, 20000000, "Выше среднего (10-20 млн)"),
        (20000000, 999999999, "Премиум (> 20 млн)")
    ]
    for min_p, max_p, label in ranges:
        count = sum(1 for p in prices if min_p <= p < max_p)
        if count > 0:
            print(f"  {label}: {count} апартаментов")

    avg_price = sum(prices) / len(prices)
    print(f"\n  Средняя цена: {avg_price:,.0f} VND (~${avg_price/25000:.0f})")
    print(f"  Минимум: {min(prices):,} VND")
    print(f"  Максимум: {max(prices):,} VND")

    # Amenities
    print(f"\n{'='*70}")
    print("✨ УДОБСТВА")
    print('='*70)
    furnished_count = sum(1 for apt in apartments if apt.furnished)
    balcony_count = sum(1 for apt in apartments if apt.balcony)
    parking_count = sum(1 for apt in apartments if apt.parking)
    elevator_count = sum(1 for apt in apartments if apt.elevator)
    ac_count = sum(1 for apt in apartments if apt.air_conditioning)
    pets_count = sum(1 for apt in apartments if apt.pets_allowed)

    total = len(apartments)
    print(f"  Меблированных: {furnished_count}/{total} ({furnished_count/total*100:.0f}%)")
    print(f"  С балконом: {balcony_count}/{total} ({balcony_count/total*100:.0f}%)")
    print(f"  С парковкой: {parking_count}/{total} ({parking_count/total*100:.0f}%)")
    print(f"  С лифтом: {elevator_count}/{total} ({elevator_count/total*100:.0f}%)")
    print(f"  С кондиционером: {ac_count}/{total} ({ac_count/total*100:.0f}%)")
    print(f"  Разрешены питомцы: {pets_count}/{total}")

    # Featured apartments
    print(f"\n{'='*70}")
    print("⭐ ИЗБРАННЫЕ АПАРТАМЕНТЫ")
    print('='*70)

    # Most expensive
    most_expensive = max(apartments, key=lambda x: x.price if x.price else 0)
    print(f"\n💎 Самый дорогой:")
    print(f"   {most_expensive.title}")
    print(f"   {most_expensive.price:,} VND | {most_expensive.rooms} комн. | {most_expensive.area_m2} м²")
    print(f"   {most_expensive.city}, {most_expensive.district}")

    # Cheapest
    cheapest = min(apartments, key=lambda x: x.price if x.price else float('inf'))
    print(f"\n💵 Самый доступный:")
    print(f"   {cheapest.title}")
    print(f"   {cheapest.price:,} VND | {cheapest.rooms} комн. | {cheapest.area_m2} м²")
    print(f"   {cheapest.city}, {cheapest.district}")

    # Largest
    largest = max(apartments, key=lambda x: x.area_m2 if x.area_m2 else 0)
    print(f"\n🏠 Самый просторный:")
    print(f"   {largest.title}")
    print(f"   {largest.area_m2} м² | {largest.rooms} комн. | {largest.price:,} VND")
    print(f"   {largest.city}, {largest.district}")

    # Special types
    special_types = [apt for apt in apartments if apt.apartment_type in ['duplex', 'penthouse', 'studio']]
    if special_types:
        print(f"\n🌟 Особые типы:")
        for apt in special_types:
            apt_type = apt.apartment_type.title()
            print(f"   {apt_type}: {apt.title[:50]}... ({apt.price:,} VND)")

    # Filtering examples
    print(f"\n{'='*70}")
    print("🔍 ПРИМЕРЫ ФИЛЬТРАЦИИ")
    print('='*70)

    # Affordable studios
    studios = scraper.filter_by_rooms(apartments, min_rooms=1, max_rooms=1)
    affordable_studios = scraper.filter_by_price(studios, min_price=0, max_price=8000000)
    print(f"\n📌 Студии до 8 млн VND: {len(affordable_studios)}")
    for apt in affordable_studios:
        print(f"   {apt.title[:45]}... - {apt.price:,} VND ({apt.city})")

    # 2BR furnished
    two_br = scraper.filter_by_rooms(apartments, min_rooms=2, max_rooms=2)
    two_br_furnished = scraper.filter_furnished(two_br, furnished=True)
    print(f"\n📌 Меблированные 2-комнатные: {len(two_br_furnished)}")
    for apt in two_br_furnished:
        print(f"   {apt.title[:45]}... - {apt.price:,} VND ({apt.city})")

    # Luxury (3+ rooms, 20M+)
    luxury = scraper.filter_by_rooms(apartments, min_rooms=3)
    luxury = scraper.filter_by_price(luxury, min_price=20000000)
    print(f"\n📌 Премиум (3+ комн., от 20 млн): {len(luxury)}")
    for apt in luxury:
        building = f" - {apt.building_name}" if apt.building_name else ""
        print(f"   {apt.title[:40]}...{building} - {apt.price:,} VND")

    # Export
    print(f"\n{'='*70}")
    print("💾 ЭКСПОРТ")
    print('='*70)

    Path("data").mkdir(exist_ok=True)
    scraper.dump_to_json(apartments, "data/extended_demo_apartments.json")
    scraper.dump_to_csv(apartments, "data/extended_demo_apartments.csv")

    print(f"\n✅ JSON: data/extended_demo_apartments.json")
    print(f"✅ CSV: data/extended_demo_apartments.csv")

    print(f"\n{'='*70}")
    print("📖 КАК ЗАПУСТИТЬ РЕАЛЬНЫЙ ПАРСИНГ")
    print('='*70)
    print("""
В окружении с доступом к интернету выполните:

1. Простой запуск:
   export PYTHONPATH=src
   python -m chotot.apartment_cli --city danang --pages 3

2. С фильтрами:
   python -m chotot.apartment_cli --city hcm --min-rooms 2 \\
       --max-price 15000000 --pages 5 --furnished-only

3. Через bash-скрипт:
   CITY=danang PAGES=5 MIN_ROOMS=2 ./scripts/scrape_apartments.sh

4. Экспорт в CSV:
   python -m chotot.apartment_cli --city hanoi --format csv \\
       --output hanoi_apartments.csv --pages 3

Примечание: В текущем Docker окружении нет доступа к интернету.
Запустите парсер в среде с интернет-соединением для получения
реальных данных из API Chotot.
""")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
