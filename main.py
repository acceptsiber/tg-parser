from ast import Await
import json
import re
from typing import Dict, List, Union
import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import logging
import requests

from json_parser import parse_message

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

template_json = {
    "type": "1",
    "user": "608",
    "object_type": "5",
    "object_fields": [
        {
            "id": "896",
            "title": "Цена",
            "field_type": "number",
            "data": {"value": "250000"},
            "options": [],
            "required": True,
        },
        {
            "id": "951",
            "title": "Общая площадь",
            "field_type": "number",
            "data": {"value": "360"},
            "options": [],
            "required": False,
        },
        {
            "id": "869",
            "title": "Адрес объекта",
            "field_type": "address",
            "data": {"value": "Узбекистан, Ташкент, ул. Циалковская"},
            "options": [],
            "required": False,
        },
        {
            "id": "871",
            "title": "Описание",
            "field_type": "rich_text",
            "data": {
                "value": "🏡Продается дом в Мирзо-Улугбекском районе! 🌍Адрес: Ул. Циалковская 🔵соток: 3,6 🔴комнат: 11 🟠этаж: 2 🟢общая площадь: 360 кв.м 💰Цена: 250 000$ ☎️ (99)729-49-91"
            },
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
            "id": "992",
            "title": "Удобства",
            "field_type": "text",
            "data": {"value": "летняя кухня"},
            "options": [],
            "required": False,
        },
        {
            "id": "981",
            "title": "Удобства",
            "field_type": "list",
            "data": {"value": "Дом"},
            "options": [],
            "required": False,
        },
        {
            "id": "990",
            "title": "Санузел",
            "field_type": "list",
            "data": {"value": "в доме"},
            "options": [],
            "required": False,
        },
        {
            "id": "991",
            "title": "Душ",
            "field_type": "list",
            "data": {"value": "В доме"},
            "options": [],
            "required": False,
        },
        {
            "id": "1135",
            "title": "Количество комнат",
            "field_type": "number",
            "data": {"value": "11"},
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
                        "0": {
                            "image": "/images/objects/19105/faa8f99cf04a007d8d845d690ea361ef.png",
                            "thumb": "/images/objects/19105/thumb_faa8f99cf04a007d8d845d690ea361ef.png",
                        }
                    }
                ]
            },
            "options": [],
            "required": False,
        },
    ],
}

API_URL = "https://hata.uz/api/object/"
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwOTMzMTI3LCJpYXQiOjE3NTA4NDY3MjcsImp0aSI6ImZkN2VjYWE5MDVkYTRlYzlhMGNhNDdkN2NiNmVhOTVlIiwidXNlcl9pZCI6NjA4fQ.J6JTgb1dxNvd6DDTmxcx94RqblDE5xO3R1G7FPwu0u0"
# Заголовки для запроса
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    # "Content-Type": "multipart/form-data",
}


class TelegramParser:
    def __init__(self, client: TelegramClient):
        self.client = client

    async def get_messages(
        self, entity: str | int, limit: int = 100
    ) -> List[Dict[str, str]]:
        """Gets messages with media files."""
        messages: List[Dict[str, str]] = []
        messages_data = await self.client.get_messages(entity, limit=limit)
        for message in messages_data:

            first_line = message.text.split("\n")[0].strip()
            message_id = (
                first_line.split()[0]
                if first_line and len(first_line.split()) > 0
                else "No ID"
            )

            messages.append(
                {
                    "telegram_id": message.id,
                    "id": re.sub(r"\*", "", message_id),
                    "message": re.sub(r"\s+", " ", message.message).strip(),
                    "photo": message.media,
                }
            )

        return messages

    async def group_objects(
        self, objects
    ) -> List[Dict[str, Union[str, List[MessageMediaPhoto]]]]:
        grouped = []
        current_group = {"message": "", "photos": []}

        for obj in objects:
            try:
                if obj["message"]:
                    current_group["message"] = obj
                    current_group["photos"].append(obj["photo"])
                    grouped.append(current_group)
                    current_group = {"message": "", "photos": []}
                else:
                    current_group["photos"].append(obj["photo"])
            except:
                continue

        return grouped

    async def download_photos(
        self, grouped_message: List[Dict[str, Union[str, List[MessageMediaPhoto]]]]
    ):
        os.makedirs("photos", exist_ok=True)
        tasks = []
        for message in grouped_message:
            for photo in message.get("photos"):
                if not photo:
                    continue

                # Проверяем тип медиа
                if isinstance(photo, MessageMediaPhoto):
                    try:
                        filename = os.path.join(
                            "photos",
                            f"{photo.photo.id}.jpg",
                        )
                        task = asyncio.create_task(
                            self.client.download_media(photo, file=filename)
                        )
                        tasks.append(task)
                    except AttributeError as e:
                        logging.warning(f"Skipping photo due to error: {e}")
                        continue

        return await asyncio.gather(*tasks)

    async def set_photo_id_to_message(
        self, grouped_message: List[Dict[str, Union[str, List[MessageMediaPhoto]]]]
    ):
        for message in grouped_message:
            message["photos_id"] = [photo.photo.id for photo in message["photos"]]

        return grouped_message


def send_json_as_multipart(json_data, field_name="fields", headers={}):

    # Преобразуем JSON данные в строку
    json_string = json.dumps(
        json_data, ensure_ascii=False
    )  # ensure_ascii=False чтобы не было проблем с кириллицей

    # Создаем файл в памяти (не нужно записывать на диск)
    files = {
        field_name: (
            "data.json",
            json_string,
            "application/json",
        )
    }

    try:
        response = requests.post(API_URL, files=files, headers=headers)
        response.raise_for_status()
        print(f"\n\n{response.json()}\n\n")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None


async def main():
    api_id = 23128708
    api_hash = "ee3dfa7067eb520a05bfc749083f9ab0"
    phone_number = "+79130028603"
    chat_entity = "prodajadomov_mirzo_ulugbek"

    async with TelegramClient("s", api_id, api_hash) as client:
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                await client.sign_in(phone_number, input("Enter code: "))

            parser = TelegramParser(client)

            messages = await parser.get_messages(chat_entity, limit=5)

            groups = await parser.group_objects(messages)
            groups = await parser.set_photo_id_to_message(groups)
            await parser.download_photos(groups)

            print(*groups, sep="\n\n")

            parsed_messages = []
            for message in groups:
                parsed_message = await parse_message(message)
                parsed_messages.append(parsed_message)

            for parsed_message in parsed_messages:
                send_json_as_multipart(json_data=parsed_message, headers=headers)

            # print(*parsed_messages, sep="\n\n")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
