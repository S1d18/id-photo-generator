# ID Photo Generator
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Инструменты для автоматической обработки фотографий: удаление фона, обнаружение и выравнивание лица, обрезка под заданный размер. Включает Telegram-бота для обработки фото.

## Возможности

- Удаление фона с изображений (rembg)
- Обнаружение лица и глаз (OpenCV Haar Cascade)
- Автоматическое выравнивание лица по глазам
- Обрезка под фиксированный размер (990x1343 px)
- Telegram-бот для обработки фото (удаление фона + кроп)
- Пакетная генерация изображений с подписями из CSV
- GUI-интерфейс для запуска различных режимов

## Технологии

- Python 3
- OpenCV (cv2) — детекция лиц и глаз
- Pillow (PIL) — обработка изображений
- rembg — удаление фона
- aiogram 3 — Telegram бот
- Pandas — работа с CSV

## Установка

```bash
git clone https://github.com/<username>/id-photo-generator.git
cd id-photo-generator
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env`:
```
BOT_TOKEN=your-telegram-bot-token
```

## Использование

### Telegram-бот
```bash
python bot.py
```
Отправьте фото боту — он удалит фон и обрежет по лицу.

### Удаление фона (GUI)
```bash
python rem_bg.py
```

### Обрезка по лицу (GUI)
```bash
python Photo_img.py
```

### Генерация подписей из CSV
```bash
python main_csv.py
```

## Структура проекта

| Файл | Описание |
|------|----------|
| `bot.py` | Telegram-бот для обработки фото |
| `Photo_img.py` | GUI-утилита обрезки по лицу |
| `rem_bg.py` | GUI-утилита удаления фона |
| `main_csv.py` | Пакетная генерация из CSV |
| `main_csv_1pic.py` | Генерация подписей из CSV |
| `app.py` | GUI-лаунчер всех режимов |
