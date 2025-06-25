from copy import deepcopy
import json
import os
import re

from images import image_to_base64


async def remove_emojis(text):
    # Регулярное выражение для удаления смайликов и других emoji
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


async def parse_message(tg_data):
    # Извлекаем данные из сообщения
    message = tg_data["message"]["message"]
    telegram_id = tg_data["message"]["telegram_id"]
    photos_id = tg_data.get("photos_id", [])

    # Парсим данные с помощью регулярных выражений
    price_match = re.search(r"💰Цена: ([0-9, ]+)\$", message)
    area_match = re.search(r"🔶общая площадь: (\d+)", message)
    address_match = re.search(r"🌍Адрес: (.+?) 🔶", message) or re.search(
        r"🌍Адрес: (.+?)💰", message
    )
    rooms_match = re.search(r"🔶комнат: (\d+)", message)
    land_match = re.search(r"🔶соток: ([0-9,]+)", message)
    floors_match = re.search(r"🔶этаж: (\d+)", message)
    state_match = re.search(r"🔶Состояние: (.+?) 💰", message)

    # Определяем тип объекта (Дом/Коттедж)
    object_type = "Дом"
    if "Коттедж" in message:
        object_type = "Коттедж"

    # Формируем JSON по вашему шаблону
    result = {
        "type": "1",
        "user": "608",
        "object_type": "5",
        "object_fields": [
            {
                "id": "896",
                "title": "Цена",
                "field_type": "number",
                "data": {
                    "value": (
                        price_match.group(1).replace(" ", "").replace(",", "")
                        if price_match
                        else "0"
                    )
                },
                "options": [],
                "required": True,
            },
            {
                "id": "951",
                "title": "Общая площадь",
                "field_type": "number",
                "data": {"value": area_match.group(1) if area_match else "0"},
                "options": [],
                "required": False,
            },
            {
                "id": "869",
                "title": "Адрес объекта",
                "field_type": "address",
                "data": {
                    "value": (
                        f"Узбекистан, Ташкент, {address_match.group(1)}"
                        if address_match
                        else ""
                    )
                },
                "options": [],
                "required": False,
            },
            {
                "id": "871",
                "title": "Описание",
                "field_type": "rich_text",
                "data": {"value": await remove_emojis(message)},
                "options": [],
                "required": False,
            },
            {
                "id": "883",
                "title": "Тип сделки",
                "field_type": "object_type",
                "data": {"value": "1"},
                "options": [],
                "required": True,
            },
            {
                "id": "981",
                "title": "Удобства",
                "field_type": "list",
                "data": {"value": object_type},
                "options": [],
                "required": False,
            },
            {
                "id": "1135",
                "title": "Количество комнат",
                "field_type": "number",
                "data": {"value": rooms_match.group(1) if rooms_match else "0"},
                "options": [],
                "required": False,
            },
            {
                "id": "882",
                "title": "Фотографии",
                "field_type": "photo",
                "data": {
                    "value": [
                        {
                            str(i): (
                                f"data:image/png;base64,{base64_string}"
                                if (
                                    base64_string := await image_to_base64(
                                        os.path.join("photos", f"{photo_id}.jpg")
                                    )
                                )
                                else None
                            )
                        }
                        for i, photo_id in enumerate(photos_id)
                    ]
                },
                "options": [],
                "required": False,
            },
        ],
    }

    return result
