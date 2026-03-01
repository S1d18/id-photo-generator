import random
import os
import csv
from PIL import Image, ImageDraw, ImageFont
import unidecode

# Общие настройки
settings = {
    'fonts_folder': 'fonts',               # Путь к папке со шрифтами
    'output_folder': 'D:/PSD/podpis',      # Папка, куда сохраняем результат
    'image_size': (2027, 1027),            # Общий размер изображения (width, height)
    'text_area_size': (1927, 900),         # Область, куда вписываем текст
    'text_color': (0, 0, 0, 255),          # Цвет текста (R, G, B, A)
}

# Настройки шрифтов
font_settings = {
    'Fonts2.ttf': {
        'font_size': 1000,
        'text_thickness': 4,
        'vertical_offset_range': (-200, -150),
        'horizontal_offset': 10,
    },
    'Fonts3.ttf': {
        'font_size': 500,
        'text_thickness': 5,
        'vertical_offset_range': (-20, -10),
        'horizontal_offset': -100,
    }
}

def determine_text_spacing(text_length):
    """
    Определяет text_spacing в зависимости от длины текста.
    """
    if text_length > 5:
        return random.randint(-50, -40)
    else:
        return random.randint(-20, -5)

def apply_random_case_modification(text):
    """
    Случайно изменяет регистр первой буквы на маленький или любой буквы на большой.
    """
    if random.random() < 0.5:
        # Сделать первую букву маленькой
        return text[0].lower() + text[1:]
    else:
        # Сделать случайную букву большой
        index = random.randint(0, len(text) - 1)
        return text[:index] + text[index].upper() + text[index + 1:]

def fit_font_to_area(text, font_path, initial_font_size, text_thickness, max_width, margin=50):
    """
    Подбирает размер шрифта так, чтобы текст гарантированно влез по ширине,
    учитывая "обводку" (text_thickness).
    """
    temp_image = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp_image)

    current_size = initial_font_size
    while True:
        font = ImageFont.truetype(font_path, current_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Учтём, что обводка даёт +2*text_thickness по бокам
        effective_text_width = text_width + 2 * text_thickness
        max_width_with_margin = max_width - margin

        if effective_text_width <= max_width_with_margin:
            return font  # Уместилось — возвращаем
        else:
            # Уменьшаем шрифт пропорционально
            scale_factor = max_width_with_margin / effective_text_width
            new_size = int(current_size * scale_factor)
            if new_size >= current_size:
                new_size = current_size - 1
            if new_size < 10:
                new_size = 10  # нижняя граница
            if new_size >= current_size:
                return font  # если не можем уменьшить
            current_size = new_size

def create_handwritten_image(text, font_path, font_size, text_spacing, text_thickness,
                             vertical_offset, horizontal_offset):
    """
    Создаёт изображение с "рукописным" текстом (обводкой), располагая его
    по центру заданной области.
    """
    max_width = settings['text_area_size'][0]

    # 1) Подбираем размер шрифта
    font = fit_font_to_area(
        text=text,
        font_path=font_path,
        initial_font_size=font_size,
        text_thickness=text_thickness,
        max_width=max_width,
        margin=50
    )

    # 2) Создаем итоговое изображение
    image = Image.new('RGBA', settings['image_size'], (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 3) Считаем bbox с уже подобранным шрифтом
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Позиция области для текста
    area_left_top = (
        (settings['image_size'][0] - settings['text_area_size'][0]) // 2,
        (settings['image_size'][1] - settings['text_area_size'][1]) // 2
    )

    # Центрируем текст внутри text_area_size
    text_position = (
        area_left_top[0] + (settings['text_area_size'][0] - text_width) // 2 + horizontal_offset,
        area_left_top[1] + (settings['text_area_size'][1] - text_height) // 2 + vertical_offset
    )

    # 4) Рисуем "обводку" для каждой буквы
    for offset_x in range(-text_thickness, text_thickness + 1):
        for offset_y in range(-text_thickness, text_thickness + 1):
            if offset_x == 0 and offset_y == 0:
                continue
            current_position = text_position
            for char in text:
                char_bbox = draw.textbbox(current_position, char, font=font)
                char_width = char_bbox[2] - char_bbox[0]
                draw.text(
                    (current_position[0] + offset_x, current_position[1] + offset_y),
                    char,
                    font=font,
                    fill=settings['text_color']
                )
                current_position = (current_position[0] + char_width + text_spacing,
                                    current_position[1])

    # 5) Рисуем сам текст поверх обводки
    current_position = text_position
    for char in text:
        char_bbox = draw.textbbox(current_position, char, font=font)
        char_width = char_bbox[2] - char_bbox[0]
        draw.text(current_position, char, font=font, fill=settings['text_color'])
        current_position = (current_position[0] + char_width + text_spacing,
                            current_position[1])

    return image

def main():
    csv_path = r'D:\PSD\data.csv'

    # 1) Считываем все записи CSV в список
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        records = list(reader)

    total = len(records)
    # 2) Узнаём, сколько нужно строк для Fonts2.ttf (10%)
    needed_for_fonts2 = int(round(0.1 * total))
    if needed_for_fonts2 < 1 and total > 0:
        needed_for_fonts2 = 1

    # 3) Случайно выбираем индексы, где будем использовать Fonts2.ttf
    all_indices = list(range(total))
    fonts2_indices = set(random.sample(all_indices, needed_for_fonts2))

    # Убедимся, что папка для сохранения есть (если нет, то создаём)
    os.makedirs(settings['output_folder'], exist_ok=True)

    # 4) Перебираем строки, для каждой генерируем 1 картинку
    for i, row in enumerate(records):
        id_ = row['id']
        first_name = row['First_name']
        last_name = row['Last_name']

        # 20% случаев добавляем первую букву
        if random.random() < 0.2:
            combined = last_name + first_name[0]
        else:
            combined = last_name

        # Заменяем "проблемные" символы
        text_to_draw = unidecode.unidecode(combined)

        # Применяем случайное изменение регистра
        text_to_draw = apply_random_case_modification(text_to_draw)

        # Выбираем шрифт: Fonts2.ttf или Fonts3.ttf
        if i in fonts2_indices:
            chosen_font = 'Fonts2.ttf'
        else:
            chosen_font = 'Fonts3.ttf'

        # Достаём данные из font_settings
        f_set = font_settings[chosen_font]
        f_size = f_set['font_size']
        t_thickness = f_set['text_thickness']

        # Генерируем random vertical_offset из заданного диапазона
        vo_min, vo_max = f_set['vertical_offset_range']
        v_offset = random.randint(vo_min, vo_max)

        # horizontal_offset — берём из словаря
        h_offset = f_set['horizontal_offset']

        # Определяем text_spacing на основе длины текста
        t_spacing = determine_text_spacing(len(text_to_draw))

        # Путь к файлу шрифта
        font_path = os.path.join(settings['fonts_folder'], chosen_font)

        # Генерируем изображение
        image = create_handwritten_image(
            text=text_to_draw,
            font_path=font_path,
            font_size=f_size,
            text_spacing=t_spacing,
            text_thickness=t_thickness,
            vertical_offset=v_offset,
            horizontal_offset=h_offset
        )

        if image:
            # Сохраняем
            output_filename = f"{id_}.png"
            output_path = os.path.join(settings['output_folder'], output_filename)
            image.save(output_path, format='PNG')
            print(f"Сохранено изображение: {output_path} | Шрифт={chosen_font}, v_offset={v_offset}, t_spacing={t_spacing}")

if __name__ == "__main__":
    main()
