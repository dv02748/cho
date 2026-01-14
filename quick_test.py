#!/usr/bin/env python3
"""Quick test script to demonstrate apartment parser with real data."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chotot.apartment_service import ApartmentScraper
from chotot.config import QueryConfig, ScraperConfig


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

    if apt.building_name:
        print(f"🏠 Здание: {apt.building_name}")

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

    print(f"📍 Адрес: {apt.address}" if apt.address else "📍 Адрес: не указан")
    print(f"🌆 Город: {apt.city}" if apt.city else "🌆 Город: не указан")
    print(f"🏘️  Район: {apt.district}" if apt.district else "🏘️  Район: не указан")

    if apt.contact_name or apt.phone:
        print(f"📞 Контакт: {apt.contact_name or ''} {apt.phone or ''}".strip())

    print(f"🔗 URL: {apt.url}")
    print(f"📷 Фото: {len(apt.images)} шт." if apt.images else "📷 Фото: нет")


def main():
    """Run quick test and display results."""
    print("\n" + "="*70)
    print("БЫСТРЫЙ ТЕСТ ПАРСЕРА АПАРТАМЕНТОВ CHOTOT")
    print("="*70)
    print("\n🔍 Ищем апартаменты в Дананге (region_v2=32)...")
    print("⏳ Категория: аренда апартаментов (cg=1000, cgr=1010)")
    print("📄 Лимит: 3 результата\n")

    # Configure for Da Nang apartments
    query = QueryConfig(
        region_v2=32,  # Da Nang
        cg=1000,       # Real Estate
        cgr=1010,      # Apartment rentals
        limit=3        # Only 3 results
    )

    config = ScraperConfig(
        query=query,
        delay_seconds=0.5,
        max_pages=1,
        trust_env_proxies=False  # Disable proxy
    )

    scraper = ApartmentScraper(config)

    try:
        print("⚙️  Запускаем парсер...")
        apartments = scraper.scrape(max_pages=1)

        if not apartments:
            print("\n❌ Апартаменты не найдены. Возможно:")
            print("   - Нет доступных объявлений в данный момент")
            print("   - Проблемы с сетью или API Chotot")
            print("   - Неверные параметры категории")
            return

        print(f"\n✅ Успешно! Найдено апартаментов: {len(apartments)}")

        # Display first 3 results
        for i, apt in enumerate(apartments[:3], 1):
            format_apartment(apt, i)

        # Statistics
        print(f"\n{'='*70}")
        print("📊 СТАТИСТИКА")
        print('='*70)

        # Room distribution
        rooms_with_data = [apt for apt in apartments if apt.rooms]
        if rooms_with_data:
            avg_rooms = sum(apt.rooms for apt in rooms_with_data) / len(rooms_with_data)
            print(f"Средн. комнат: {avg_rooms:.1f}")

        # Price statistics
        prices = [apt.price for apt in apartments if apt.price]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"Средн. цена: {avg_price:,.0f} VND")
            print(f"Мин. цена: {min(prices):,} VND")
            print(f"Макс. цена: {max(prices):,} VND")

        # Furnished count
        furnished_count = sum(1 for apt in apartments if apt.furnished)
        print(f"Меблированных: {furnished_count}/{len(apartments)}")

        # Save to file
        output_file = "data/quick_test_apartments.json"
        Path("data").mkdir(exist_ok=True)
        scraper.dump_to_json(apartments, output_file)
        print(f"\n💾 Результаты сохранены в: {output_file}")

        print(f"\n{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Ошибка при парсинге: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
