# userbot/core.py

import asyncio
from telethon import TelegramClient, events, Button
from config import get_config, get_stats, save_stats
import re

API_ID = 123456  # Замените на ваш API ID
API_HASH = 'your_api_hash'  # Замените на ваш API Hash
SESSION_NAME = 'userbot_session'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Паттерны и ключи
ORDER_LIST_TRIGGER = "Список текущих заказов"
ORDER_MESSAGE_REGEX = r"Заказ №(\d+).+?Локация: (.*?)\n.+?Объем: (\d+)т.+?Цена: (\d+) KZT/т"

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    config = get_config()
    stats = get_stats()

    if not config["enabled"]:
        return

    # Триггер на входящее уведомление от биржи
    if ORDER_LIST_TRIGGER in event.raw_text:
        await event.click(text=ORDER_LIST_TRIGGER)

    # Обработка входящих сообщений с заказами
    match = re.search(ORDER_MESSAGE_REGEX, event.raw_text)
    if match:
        order_id = match.group(1)
        location = match.group(2).strip()
        volume = int(match.group(3))
        price = int(match.group(4))

        # Пропустить, если заказ уже обработан
        if order_id in stats["cache"]:
            return

        # Фильтрация
        target = config["target"]
        if target["location"] != "-" and target["location"] != location:
            stats["filtered_out"] += 1
        elif volume < target["min_volume"] or volume > target["max_volume"]:
            stats["filtered_out"] += 1
        elif price < target["min_price"]:
            stats["filtered_out"] += 1
        else:
            # Прошёл фильтр, ищем кнопку "Возьму"
            for btn_row in event.buttons:
                for btn in btn_row:
                    if btn.text == "Возьму":
                        await event.click(button=btn)
                        await handle_followup(event, order_id, volume, price, config, stats)
                        break
        stats["cache"].append(order_id)
        save_stats(stats)


async def handle_followup(event, order_id, volume, price, config, stats):
    adaptive = config["adaptive"]
    prop = config["proposal"]

    # Ожидаем следующее сообщение от биржи после нажатия "Возьму"
    response = await client.wait_for(events.NewMessage(from_users=event.chat_id), timeout=10)

    if "сколько тонн" in response.raw_text.lower():
        to_send = prop["tons"] if not adaptive else min(volume, prop["tons"])
        await response.respond(str(to_send))
        response = await client.wait_for(events.NewMessage(from_users=event.chat_id), timeout=10)

    if "цену за тонну" in response.raw_text.lower():
        to_send = prop["price"] if not adaptive else max(config["target"]["min_price"], price)
        await response.respond(str(to_send))
        response = await client.wait_for(events.NewMessage(from_users=event.chat_id), timeout=10)

    if "уже есть предложение" in response.raw_text.lower():
        if config["dumping"]:
            for btn_row in response.buttons:
                for btn in btn_row:
                    if btn.text == "Возьму":
                        await response.click(button=btn)
                        stats["taken_with_dump"] += 1
                        return
        else:
            for btn_row in response.buttons:
                for btn in btn_row:
                    if btn.text == "Откажусь":
                        await response.click(button=btn)
                        stats["rejected"] += 1
                        return
    else:
        stats["taken_without_dump"] += 1


async def run_userbot():
    await client.start()
    print("[UserBot] Запущен")
    await client.run_until_disconnected()
