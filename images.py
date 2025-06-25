import asyncio
import aiofiles
import base64
import os


async def image_to_base64(image_path: str) -> str:
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
            base64_string = base64.b64encode(image_data).decode("utf-8")
            return base64_string
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден: {image_path}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке файла {image_path}: {e}")
        return None
