import tkinter as tk
import os
import subprocess
import sys

# Пути к скриптам
PHOTO_IMG_SCRIPT = "Photo_img.py"
REM_BG_SCRIPT = "rem_bg.py"

def run_script(script_path):
    """
    Запускает указанный скрипт Python.
    """
    if os.path.exists(script_path):
        subprocess.Popen([sys.executable, script_path])  # Использует текущий интерпретатор Python
    else:
        print(f"Скрипт {script_path} не найден.")

def main():
    """
    Создаёт окно с выбором действий.
    """
    root = tk.Tk()
    root.title("Выбор действия")

    # Создание кнопок
    btn_face_crop = tk.Button(
        root, text="Обрезка лиц (Photo_img.py)", command=lambda: run_script(PHOTO_IMG_SCRIPT)
    )
    btn_face_crop.pack(pady=10, padx=20)

    btn_photo_crop = tk.Button(
        root, text="Обрезка фото (rem_bg.py)", command=lambda: run_script(REM_BG_SCRIPT)
    )
    btn_photo_crop.pack(pady=10, padx=20)

    # Запуск главного цикла
    root.mainloop()

if __name__ == "__main__":
    main()
