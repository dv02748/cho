from chotot_parser.parser import AdParser


def test_parse_listing_payload():
    payload = {
        "ads": [
            {
                "list_id": 1,
                "subject": "Cho thuê căn hộ gần biển",
                "price": 12000000,
                "size": 60,
                "ward_name": "Phước Mỹ",
                "area_name": "Sơn Trà",
                "region_name": "Đà Nẵng",
                "body": "2 phòng ngủ, full nội thất",
                "list_time": 1700000000,
                "ad_link": "https://www.chotot.com/abcd",
                "images": ["https://image1"],
                "contact": {"name": "Anh A", "phone": "0905"},
            }
        ]
    }

    ads = list(AdParser.parse_listing_payload(payload))

    assert len(ads) == 1
    ad = ads[0]
    assert ad.id == 1
    assert ad.location == "Phước Mỹ, Sơn Trà, Đà Nẵng"
    assert ad.images == ["https://image1"]
