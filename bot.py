import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
import asyncio
import cv2
import math
import numpy as np
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ContentType, FSInputFile
from aiogram.filters import Command
from rembg import remove
from PIL import Image



# Папка для временного хранения файлов
TEMP_FOLDER = "temp_files"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Пути к XML-файлам каскадов (лицо + глаза)
FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"
EYE_CASCADE_PATH = "haarcascade_eye.xml"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


def detect_face_and_eyes(np_rgb):
    """
    Ищет лицо и глаза (Haar Cascades).
    Возвращает список (x, y, w, h, eyes_centers).
    """
    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
    eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)

    gray = cv2.cvtColor(np_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    results = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y: y + h, x: x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.2, minNeighbors=5)

        eyes_centers = []
        for (ex, ey, ew, eh) in eyes:
            cx = int(x + ex + ew // 2)
            cy = int(y + ey + eh // 2)
            eyes_centers.append((cx, cy))

        results.append((x, y, w, h, eyes_centers))

    return results


def rotate_rgba(np_rgba, angle, center=None):
    """
    Поворачивает 4-канальное RGBA-изображение (NumPy) на угол angle (в градусах).
    angle > 0 — против часовой.
    """
    h, w = np_rgba.shape[:2]
    if center is None:
        center = (w // 2, h // 2)
    cx, cy = map(int, center)
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rotated = cv2.warpAffine(np_rgba, M, (w, h), flags=cv2.INTER_CUBIC)
    return rotated


def remove_bg_and_straighten(input_path, output_path, final_size=(990, 1343), expand_ratio=0.5):
    """
    Удаляет фон, выравнивает лицо по глазам, обрезает, масштабирует, сохраняет PNG.
    """
    with Image.open(input_path) as pil_img:
        rgba_no_bg = remove(pil_img)

    np_rgba = np.array(rgba_no_bg)
    np_rgb = np_rgba[..., :3]

    detections = detect_face_and_eyes(np_rgb)
    if not detections:
        raise ValueError("Не найдено ни одного лица (Haar Cascade).")

    x, y, w, h, eyes_centers = detections[0]
    if len(eyes_centers) < 2:
        print("Меньше 2 глаз. Поворот пропускаем.")
        angle = 0
        cx = x + w // 2
        cy = y + h // 2
        np_rgba_rotated = rotate_rgba(np_rgba, angle, (cx, cy))
    else:
        (x1, y1), (x2, y2) = eyes_centers[:2]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dx = x2 - x1
        dy = y2 - y1
        angle = math.degrees(math.atan2(dy, dx))
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        np_rgba_rotated = rotate_rgba(np_rgba, angle, (cx, cy))

    # Повторный детект лица на повернутом изображении
    np_rgb_rot = np_rgba_rotated[..., :3]
    detections2 = detect_face_and_eyes(np_rgb_rot)
    if not detections2:
        print("Лицо не найдено после выравнивания. Используем старые координаты.")
        face_x, face_y, face_w, face_h = x, y, w, h
    else:
        face_x, face_y, face_w, face_h, _ = detections2[0]

    new_w = int(face_w * (1 + expand_ratio))
    new_h = int(face_h * (1 + expand_ratio))
    face_cx = face_x + face_w // 2
    face_cy = face_y + face_h // 2

    X1 = max(0, face_cx - new_w // 2)
    Y1 = max(0, face_cy - new_h // 2)
    X2 = min(np_rgba_rotated.shape[1], face_cx + new_w // 2)
    Y2 = min(np_rgba_rotated.shape[0], face_cy + new_h // 2)

    cropped_rgba = np_rgba_rotated[Y1:Y2, X1:X2, :]

    # Приводим к нужной пропорции (без искажений)
    desired_w, desired_h = final_size
    desired_ratio = desired_w / desired_h
    crop_h, crop_w = cropped_rgba.shape[:2]
    current_ratio = crop_w / crop_h

    if current_ratio > desired_ratio:
        new_w2 = int(crop_h * desired_ratio)
        diff_w = crop_w - new_w2
        x_start = diff_w // 2
        x_end = x_start + new_w2
        cropped_rgba = cropped_rgba[:, x_start:x_end, :]
    elif current_ratio < desired_ratio:
        new_h2 = int(crop_w / desired_ratio)
        diff_h = crop_h - new_h2
        y_start = diff_h // 2
        y_end = y_start + new_h2
        cropped_rgba = cropped_rgba[y_start:y_end, :, :]

    result_rgba = cv2.resize(cropped_rgba, final_size, interpolation=cv2.INTER_CUBIC)
    Image.fromarray(result_rgba, mode="RGBA").save(output_path, format="PNG")


@router.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    Отправляет приветственное сообщение.
    """
    await message.answer(
        "Привет! Отправьте мне изображение, и я пришлю два варианта обработки:\n"
        "1. Удаление фона\n2. Обрезка лица"
    )


@router.message(lambda message: message.content_type in {ContentType.PHOTO, ContentType.DOCUMENT})
async def handle_image(message: types.Message):
    """
    Обрабатывает изображения: удаляет фон и обрезает лицо.
    """
    try:
        # Скачиваем файл
        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.document and message.document.mime_type.startswith("image/"):
            file_id = message.document.file_id
        else:
            await message.reply("Пожалуйста, отправьте изображение.")
            return

        file = await bot.get_file(file_id)
        input_path = os.path.join(TEMP_FOLDER, f"{file.file_id}.jpg")
        bg_removed_path = os.path.join(TEMP_FOLDER, f"{file.file_id}_bg_removed.png")
        face_cropped_path = os.path.join(TEMP_FOLDER, f"{file.file_id}_face_cropped.png")
        await bot.download_file(file.file_path, input_path)

        # Удаление фона
        with Image.open(input_path) as img:
            result = remove(img)
            result.save(bg_removed_path, format="PNG")

        # Обрезка лица
        remove_bg_and_straighten(input_path, face_cropped_path)

        # Отправляем результаты
        await message.answer_document(FSInputFile(bg_removed_path))
        await message.answer_document(FSInputFile(face_cropped_path))

    except Exception as e:
        await message.reply(f"Ошибка при обработке изображения: {e}")

    finally:
        # Удаляем временные файлы
        for path in [input_path, bg_removed_path, face_cropped_path]:
            if os.path.exists(path):
                os.remove(path)


async def main():
    """
    Запуск бота.
    """
    dp.include_router(router)  # Подключение маршрутизатора
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
