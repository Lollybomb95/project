# userbot/utils.py
import re
from config import save_stats

# Пример шаблонов, адаптируй под точные формулировки заказов
ORDER_ID_REGEX = r"Заказ №(\d+)"
VOLUME_REGEX = r"Об[ъеё]м[:\s]*(\d+) ?т"
PRICE_REGEX = r"Цена[:\s]*(\d+) ?KZT/т"
LOCATION_REGEX = r"Локац[ияи][:\s]*(\w+)"

def extract_order_data(message) -> dict:
    text = message.message
    order_id = int(re.search(ORDER_ID_REGEX, text).group(1)) if re.search(ORDER_ID_REGEX, text) else 0
    volume = int(re.search(VOLUME_REGEX, text).group(1)) if re.search(VOLUME_REGEX, text) else 0
    price = int(re.search(PRICE_REGEX, text).group(1)) if re.search(PRICE_REGEX, text) else 0
    location = re.search(LOCATION_REGEX, text)
    location = location.group(1).lower() if location else ""

    return {
        "order_id": order_id,
        "volume": volume,
        "price": price,
        "location": location
    }

def order_matches_target(order: dict, target: dict) -> bool:
    if target["location"] != "-" and target["location"].lower() not in order["location"]:
        return False
    if order["volume"] < target["min_volume"] or order["volume"] > target["max_volume"]:
        return False
    if order["price"] < target["min_price"]:
        return False
    return True

def update_cache(stats: dict, order_id: int):
    if order_id not in stats["cache"]:
        stats["cache"].append(order_id)
        # ограничим длину кэша до 300 последних записей
        if len(stats["cache"]) > 300:
            stats["cache"] = stats["cache"][-300:]
        save_stats(stats)
