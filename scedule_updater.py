import json
import os
import tempfile


def scedule_updater(link, school):
    file_path = "./static/DB/scedule.json"
    dir_path = os.path.dirname(file_path)

    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Читаємо існуючі дані з файлу
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r', encoding='utf8') as file:
                data = json.load(file)
        else:
            data = {}

        # Оновлюємо дані в пам'яті
        data[school] = link

        # Створюємо тимчасовий файл і записуємо в нього дані
        # Це гарантує, що оригінальний файл не буде пошкоджений,
        # якщо процес буде перервано
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf8') as temp_file:
            json.dump(data, temp_file, indent=4, ensure_ascii=False)
            temp_file_path = temp_file.name

        # Перейменовуємо тимчасовий файл, замінюючи оригінальний
        os.replace(temp_file_path, file_path)

        return "Розклад було оновлено"

    except Exception as e:
        # У разі помилки, видаляємо тимчасовий файл, якщо він був створений
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        print(f"Виникла помилка при оновленні розкладу: {e}")
        return "Виникла помилка при оновленні розкладу, спробуйте ще раз"


def scedule_reader():
    file_path = "./static/DB/scedule.json"
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}