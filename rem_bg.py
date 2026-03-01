import tkinter as tk
from tkinter import filedialog
import os
from rembg import remove
from PIL import Image

# Папка для сохранения результатов
SAVE_FOLDER = r"D:/PSD/Photo"

def remove_background(input_path, output_path):
    """
    Удаляет фон из изображения и сохраняет результат.
    """
    with Image.open(input_path) as pil_img:
        rgba_no_bg = remove(pil_img)
        rgba_no_bg.save(output_path, format="PNG")
    print(f"Сохранено: {output_path}")

def main_tk_dialog_multifile():
    """
    1) Позволяет выбрать несколько файлов
    2) Удаляет фон из каждого файла
    3) Сохраняет результат в D:/PSD/Photo
    """
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Выберите одну или несколько фотографий",
        filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All Files", "*.*")]
    )
    if not file_paths:
        print("Файлы не выбраны, выходим.")
        return

    # Создадим папку, если она не существует
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    for file_path in file_paths:
        base_name = os.path.basename(file_path)
        file_stem, _ = os.path.splitext(base_name)

        out_name = file_stem + ".png"  # результат сохраняем в PNG
        out_path = os.path.join(SAVE_FOLDER, out_name)

        print(f"\nОбрабатываем: {file_path}")
        try:
            remove_background(input_path=file_path, output_path=out_path)
        except Exception as e:
            print(f"Ошибка при обработке {file_path}: {e}")

    print("\nВсе файлы обработаны.")

if __name__ == "__main__":
    main_tk_dialog_multifile()
