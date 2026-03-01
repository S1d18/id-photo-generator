import random
import os
import csv
from PIL import Image, ImageDraw, ImageFont
import unidecode

# Ваши настройки
settings = {
    'fonts_folder': 'fonts',
    'image_size': (3291, 1673),
    'text_area_size': (2828, 1500),
    'text_color': (0, 0, 0, 255),
}

font_settings = {
    'Fonts1.ttf': {
        'font_size': 1200,
        'text_spacing': -5,
        'text_thickness': 4,
        'vertical_offset': 0,
        'horizontal_offset': 0,
    },
    'Fonts2.ttf': {
        'font_size': 1300,
        'text_spacing': -5,
        'text_thickness': 6,
        'vertical_offset': -400,
        'horizontal_offset': 10,
    },
    'Fonts3.ttf': {
        'font_size': 900,
        'text_spacing': -5,
        'text_thickness': 10,
        'vertical_offset': -10,
        'horizontal_offset': -5,
    }
}

def fit_font_to_area(text, font_path, initial_font_size, text_thickness, max_width, margin=50):
    """
    Возвращает объект шрифта (ImageFont) такого размера,
    чтобы текст гарантированно влез по ширине области max_width,
    учитывая обводку (text_thickness).
    """
    temp_image = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp_image)

    current_size = initial_font_size

    while True:
        font = ImageFont.truetype(font_path, current_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Учитываем обводку (условно + 2*thickness)
        effective_text_width = text_width + 2 * text_thickness
        max_width_with_margin = max_width - margin

        if effective_text_width <= max_width_with_margin:
            # текст умещается — возвращаем
            return font
        else:
            # вычислим коэффициент уменьшения
            scale_factor = max_width_with_margin / effective_text_width
            new_size = int(current_size * scale_factor)
            # предохраняемся от зацикливания
            if new_size >= current_size:
                new_size = current_size - 1
            if new_size < 10:
                new_size = 10
            if new_size >= current_size:
                # если не можем уменьшить, вернём текущий
                return font
            current_size = new_size


def create_handwritten_image(text, font_path, font_size, text_spacing, text_thickness,
                             vertical_offset, horizontal_offset):
    """
    Создаёт изображение с "рукописным" текстом (с имитацией толщины),
    располагая текст по центру заданной области.
    """
    max_width = settings['text_area_size'][0]

    # 1) Определяем «подходящий» шрифт, чтобы текст не вылазил за max_width
    font = fit_font_to_area(
        text=text,
        font_path=font_path,
        initial_font_size=font_size,
        text_thickness=text_thickness,
        max_width=max_width,
        margin=50  # можно подкорректировать
    )

    # 2) Теперь рисуем итоговое изображение
    image = Image.new('RGBA', settings['image_size'], (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Считаем bbox
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    area_left_top = (
        (settings['image_size'][0] - settings['text_area_size'][0]) // 2,
        (settings['image_size'][1] - settings['text_area_size'][1]) // 2
    )

    text_position = (
        area_left_top[0] + (settings['text_area_size'][0] - text_width) // 2 + horizontal_offset,
        area_left_top[1] + (settings['text_area_size'][1] - text_height) // 2 + vertical_offset
    )

    # 3) Рисуем "обводку" (имитация рукописного)
    for offset_x in range(-text_thickness, text_thickness + 1):
        for offset_y in range(-text_thickness, text_thickness + 1):
            if offset_x == 0 and offset_y == 0:
                continue
            current_position = text_position
            for char in text:
                char_bbox = draw.textbbox(current_position, char, font=font)
                char_width = char_bbox[2] - char_bbox[0]
                draw.text((current_position[0] + offset_x,
                           current_position[1] + offset_y),
                          char,
                          font=font,
                          fill=settings['text_color'])
                current_position = (current_position[0] + char_width + text_spacing,
                                    current_position[1])

    # 4) Рисуем сам текст поверх обводки
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

    font_files = [f for f in os.listdir(settings['fonts_folder']) if f.endswith('.ttf')]

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            id_ = row['id']
            first_name = row['First_name']
            last_name = row['Last_name']

            # 20% случаев добавляем первую букву
            if random.random() < 0.2:
                combined = last_name + first_name[0]
            else:
                combined = last_name

            text_to_draw = unidecode.unidecode(combined)

            for i, font_file in enumerate(font_files, start=1):
                font_path = os.path.join(settings['fonts_folder'], font_file)
                if font_file in font_settings:
                    f_size = font_settings[font_file]['font_size']
                    t_spacing = font_settings[font_file]['text_spacing']
                    t_thickness = font_settings[font_file]['text_thickness']
                    v_offset = font_settings[font_file]['vertical_offset']
                    h_offset = font_settings[font_file]['horizontal_offset']
                else:
                    f_size = 1000
                    t_spacing = -5
                    t_thickness = 4
                    v_offset = 0
                    h_offset = 0

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
                    output_filename = f"{id_}({i}).png"
                    image.save(output_filename, format='PNG')
                    print(f"Сохранено изображение: {output_filename}")

if __name__ == "__main__":
    main()
