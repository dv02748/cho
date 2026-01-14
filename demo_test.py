#!/usr/bin/env python3
"""Demo test using fixture data to show apartment parser functionality."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chotot.apartment_parser import parse_apartments
from chotot.apartment_service import ApartmentScraper
from chotot.config import ScraperConfig


def format_apartment(apt, index):
    """Format apartment data for display."""
    print(f"\n{'='*70}")
    print(f"АПАРТАМЕНТ #{index}")
    print('='*70)
    print(f"📌 Название: {apt.title}")
    print(f"🏷️  ID: {apt.ad_id}")
    print(f"💰 Цена: {apt.price:,} VND" if apt.price else "💰 Цена: не указана")
    print(f"📐 Площадь: {apt.area_m2} м²" if apt.area_m2 else "📐 Площадь: не указана")

    # Apartment-specific fields
    print(f"🛏️  Комнат: {apt.rooms}" if apt.rooms else "🛏️  Комнат: не указано")
    print(f"🚿 Ванных: {apt.bathrooms}" if apt.bathrooms else "🚿 Ванных: не указано")
    print(f"🏢 Этаж: {apt.floor}" if apt.floor else "🏢 Этаж: не указан")
    print(f"🪑 Мебель: {'Да' if apt.furnished else 'Нет'}")

    if apt.furniture_type:
        print(f"   Тип мебели: {apt.furniture_type}")

    if apt.building_name:
        print(f"🏠 Здание: {apt.building_name}")

    if apt.apartment_type:
        print(f"🏘️  Тип: {apt.apartment_type}")

    # Amenities
    amenities = []
    if apt.balcony:
        amenities.append("балкон")
    if apt.parking:
        amenities.append("парковка")
    if apt.elevator:
        amenities.append("лифт")
    if apt.air_conditioning:
        amenities.append("кондиционер")

    if amenities:
        print(f"✨ Удобства: {', '.join(amenities)}")

    if apt.direction:
        print(f"🧭 Ориентация: {apt.direction}")

    print(f"📍 Адрес: {apt.address}" if apt.address else "📍 Адрес: не указан")
    print(f"🌆 Город: {apt.city}" if apt.city else "🌆 Город: не указан")
    print(f"🏘️  Район: {apt.district}" if apt.district else "🏘️  Район: не указан")

    if apt.ward:
        print(f"   Ward: {apt.ward}")

    if apt.latitude and apt.longitude:
        print(f"🗺️  GPS: {apt.latitude}, {apt.longitude}")

    if apt.contact_name or apt.phone:
        print(f"📞 Контакт: {apt.contact_name or ''} {apt.phone or ''}".strip())

    print(f"🔗 URL: {apt.url}")
    print(f"📷 Фото: {len(apt.images)} шт." if apt.images else "📷 Фото: нет")

    if apt.description:
        desc = apt.description[:100] + "..." if len(apt.description) > 100 else apt.description
        print(f"📝 Описание: {desc}")


def main():
    """Run demo test with fixture data."""
    print("\n" + "="*70)
    print("ДЕМОНСТРАЦИЯ ПАРСЕРА АПАРТАМЕНТОВ CHOTOT")
    print("="*70)
    print("\n📂 Используем тестовые данные для демонстрации функциональности")
    print("   (реальный парсинг требует доступа к Chotot API)\n")

    # Load fixture data
    fixture_path = Path(__file__).parent / "tests" / "tests_data" / "sample_apartment_ads.json"

    if not fixture_path.exists():
        print(f"❌ Файл с тестовыми данными не найден: {fixture_path}")
        return

    with open(fixture_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    config = ScraperConfig()
    apartments = parse_apartments(raw_data, config)

    print(f"✅ Успешно распарсено: {len(apartments)} апартаментов\n")

    # Display all results
    for i, apt in enumerate(apartments, 1):
        format_apartment(apt, i)

    # Statistics
    print(f"\n{'='*70}")
    print("📊 СТАТИСТИКА")
    print('='*70)

    # Room distribution
    rooms_with_data = [apt for apt in apartments if apt.rooms]
    if rooms_with_data:
        room_counts = {}
        for apt in rooms_with_data:
            room_counts[apt.rooms] = room_counts.get(apt.rooms, 0) + 1
        print("\nРаспределение по комнатам:")
        for rooms, count in sorted(room_counts.items()):
            print(f"  {rooms} комнат(а): {count} апартамент(ов)")

    # Price statistics
    prices = [apt.price for apt in apartments if apt.price]
    if prices:
        avg_price = sum(prices) / len(prices)
        print(f"\nЦеновая статистика:")
        print(f"  Средняя: {avg_price:,.0f} VND")
        print(f"  Минимум: {min(prices):,} VND")
        print(f"  Максимум: {max(prices):,} VND")

    # Furnished count
    furnished_count = sum(1 for apt in apartments if apt.furnished)
    print(f"\nМеблировка:")
    print(f"  Меблированных: {furnished_count}/{len(apartments)} ({furnished_count/len(apartments)*100:.0f}%)")

    # Amenities
    balcony_count = sum(1 for apt in apartments if apt.balcony)
    parking_count = sum(1 for apt in apartments if apt.parking)
    elevator_count = sum(1 for apt in apartments if apt.elevator)
    ac_count = sum(1 for apt in apartments if apt.air_conditioning)

    print(f"\nУдобства:")
    print(f"  С балконом: {balcony_count}")
    print(f"  С парковкой: {parking_count}")
    print(f"  С лифтом: {elevator_count}")
    print(f"  С кондиционером: {ac_count}")

    # Test filtering
    print(f"\n{'='*70}")
    print("🔍 ДЕМОНСТРАЦИЯ ФИЛЬТРАЦИИ")
    print('='*70)

    scraper = ApartmentScraper(config)

    # Filter by rooms
    studios = scraper.filter_by_rooms(apartments, min_rooms=1, max_rooms=1)
    print(f"\nСтудии (1 комната): {len(studios)}")
    for apt in studios:
        print(f"  - {apt.title} ({apt.price:,} VND)" if apt.price else f"  - {apt.title}")

    # Filter by price
    affordable = scraper.filter_by_price(apartments, min_price=0, max_price=10000000)
    print(f"\nДоступные (до 10 млн VND): {len(affordable)}")
    for apt in affordable:
        print(f"  - {apt.title} ({apt.price:,} VND)" if apt.price else f"  - {apt.title}")

    # Filter furnished
    furnished = scraper.filter_furnished(apartments, furnished=True)
    print(f"\nМеблированные: {len(furnished)}")
    for apt in furnished:
        print(f"  - {apt.title} ({apt.rooms} комн.)" if apt.rooms else f"  - {apt.title}")

    # Export examples
    print(f"\n{'='*70}")
    print("💾 ЭКСПОРТ ДАННЫХ")
    print('='*70)

    Path("data").mkdir(exist_ok=True)

    json_file = "data/demo_apartments.json"
    scraper.dump_to_json(apartments, json_file)
    print(f"\n✅ JSON: {json_file}")

    csv_file = "data/demo_apartments.csv"
    scraper.dump_to_csv(apartments, csv_file)
    print(f"✅ CSV: {csv_file}")

    print(f"\n{'='*70}")
    print("✨ ГОТОВО!")
    print('='*70)
    print("\nДля реального парсинга используйте:")
    print("  python -m chotot.apartment_cli --city danang --pages 3")
    print("\nИли bash-скрипт:")
    print("  CITY=hcm PAGES=5 ./scripts/scrape_apartments.sh")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
