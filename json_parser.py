from copy import deepcopy
import json
import re


def remove_emojis(text):
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


def parse_message_to_json(message, template_json):
    price_match = re.search(r"Цена:\s*([\d\s]+)\$", message)
    area_match = re.search(r"общая площадь:\s*([\d]+)\s*кв\.м", message)
    address_match = re.search(r"Адрес:\s*(.*?)\s*🔶", message)
    description = message.split("☎️")[0].strip() if "☎️" in message else message
    rooms_match = re.search(r"комнат:\s*(\d+)", message)
    floors_match = re.search(r"этаж:\s*(\d+)", message)
    land_area_match = re.search(r"соток:\s*([\d,]+)", message)
    condition_match = re.search(r"Состояние:\s*(.*?)(?=💰|🔶|☎️|$)", message)

    deal_type = "1"  # по умолчанию продажа
    if any(word in message.lower() for word in ["аренда", "сдается", "аренду"]):
        deal_type = "2"

    for field in template_json["object_fields"]:
        if field["title"] == "Цена" and price_match:
            price = price_match.group(1).replace(" ", "")
            field["data"]["value"] = str(price)

        elif field["title"] == "Общая площадь" and area_match:
            field["data"]["value"] = area_match.group(1)

        elif field["title"] == "Адрес объекта" and address_match:
            field["data"][
                "value"
            ] = f"Узбекистан, Ташкент, {address_match.group(1).strip()}"

        elif field["title"] == "Описание":
            field["data"]["value"] = remove_emojis(description)

        elif field["title"] == "Тип сделки":
            field["data"]["value"] = deal_type
            
    result_json = deepcopy(template_json)
    return result_json


# Исходное сообщение
# message = "С779 🏡Продается дом в Мирзо-Улугбекском районе! 🌍Адрес: ор-р Ул. Кайнарсай 🔶соток: 2,8 🔶этаж: 2 🔶комнат: 5 🔶общая площадь: 300 кв.м 🔶Состояние: Авторский проект 💰Цена: 370 000$ ☎️ (99)729-49-91"

# # Загружаем JSON шаблон
# template_json = {
#     "type": "1",
#     "user": "608",
#     "object_type": "5",
#     "object_fields": [
#         {
#             "id": "896",
#             "title": "Цена",
#             "field_type": "number",
#             "data": {"value": "5000000"},
#             "options": [],
#             "required": True,
#         },
#         {
#             "id": "951",
#             "title": "Общая площадь",
#             "field_type": "number",
#             "data": {"value": "Узбекистан, Ташкент, Циолковский"},
#             "options": [],
#             "required": False,
#         },
#         {
#             "id": "869",
#             "title": "Адрес объекта",
#             "field_type": "address",
#             "data": {"value": "Узбекистан, Ташкент, Циолковский"},
#             "options": [],
#             "required": False,
#         },
#         {
#             "id": "871",
#             "title": "Описание",
#             "field_type": "rich_text",
#             "data": {
#                 "value": "🏡Продается дом в Мирзо-Улугбекском районе! 🌍Адрес: Ул. Циалковская 🔵соток: 3,6 🔴комнат: 11 🟠этаж: 2 🟢общая площадь: 360 кв.м 💰Цена: 250 000$ ☎️ (99)729-49-91"
#             },
#             "options": [],
#             "required": False,
#         },
#         {
#             "id": "883",
#             "title": "Тип сделки",
#             "field_type": "object_type",
#             "data": {"value": "1"},
#             "options": [],
#             "required": True,
#         },
#     ],
# }

# # Парсим сообщение и обновляем JSON
# updated_json = parse_message_to_json(message, template_json)

# # Выводим результат
# print(json.dumps(updated_json, ensure_ascii=False, indent=2))
