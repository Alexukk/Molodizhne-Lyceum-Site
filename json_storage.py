import json
import os
import shutil
from filelock import FileLock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DB_DIR = os.path.join(BASE_DIR, 'Static', 'DB')

os.makedirs(STATIC_DB_DIR, exist_ok=True)

MAIN_DATA_FILENAME = 'posts.json'
BACKUP_DATA_FILENAME = 'posts_backup.json'

# Полные пути к файлам
POSTS_FILE_PATH = os.path.join(STATIC_DB_DIR, MAIN_DATA_FILENAME)
POSTS_BACKUP_FILE_PATH = os.path.join(STATIC_DB_DIR, BACKUP_DATA_FILENAME)

POSTS_LOCK_FILE_PATH = POSTS_FILE_PATH + '.lock'
POSTS_BACKUP_LOCK_FILE_PATH = POSTS_BACKUP_FILE_PATH + '.lock'


def _read_data_from_file(file_path):
    """Внутренняя вспомогательная функция для чтения JSON из файла."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []  # Возвращаем пустой список, если файл не существует или пуст
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Warning: {file_path} does not contain a list. Returning empty list.")
                return []
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def _write_data_to_file(file_path, data):
    """Внутренняя вспомогательная функция для записи JSON в файл."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def load_posts():
    """Читает все посты из основного файла с блокировкой и логикой восстановления."""
    main_lock = FileLock(POSTS_LOCK_FILE_PATH, timeout=10)
    backup_lock = FileLock(POSTS_BACKUP_LOCK_FILE_PATH, timeout=10)

    with main_lock:
        data = _read_data_from_file(POSTS_FILE_PATH)
        if data is None:  # Основной файл поврежден, пытаемся восстановить из бэкапа
            print(f"Main data file {POSTS_FILE_PATH} corrupted. Attempting to restore from backup.")
            with backup_lock:  # Блокируем бэкап при попытке восстановления
                backup_data = _read_data_from_file(POSTS_BACKUP_FILE_PATH)
                if backup_data is not None:
                    print(f"Restoring from backup {POSTS_BACKUP_FILE_PATH}...")
                    if _write_data_to_file(POSTS_FILE_PATH, backup_data):
                        print("Restoration successful.")
                        return backup_data
                    else:
                        print("Failed to write restored data to main file.")
                else:
                    print("Backup file is also corrupted or empty. Cannot restore.")
            return []  # Возвращаем пустой список, если восстановление не удалось
        return data


def save_post(post_data: dict) -> bool:
    """
    Добавляет один пост в JSON-файл, создавая резервную копию перед записью.
    Использует блокировку файлов для безопасной работы.
    :param post_data: Словарь, представляющий один пост (с 'title', 'text', 'date' и т.д.).
    :return: True в случае успешной записи, False в случае ошибки.
    """
    if not isinstance(post_data, dict):
        print("Error: Input 'post_data' must be a dictionary.")
        return False

    main_lock = FileLock(POSTS_LOCK_FILE_PATH, timeout=10)
    backup_lock = FileLock(POSTS_BACKUP_LOCK_FILE_PATH, timeout=10)

    with main_lock:
        # 1. Загружаем текущие посты
        all_posts = _read_data_from_file(POSTS_FILE_PATH)
        if all_posts is None:  # Если основной файл поврежден при чтении
            print("Failed to read main posts file, attempting to use empty list for new post.")
            all_posts = []

        # 2. Делаем резервную копию текущего основного файла, если он существует
        if os.path.exists(POSTS_FILE_PATH) and os.path.getsize(POSTS_FILE_PATH) > 0:
            with backup_lock:  # Блокируем бэкап при создании его копии
                try:
                    shutil.copyfile(POSTS_FILE_PATH, POSTS_BACKUP_FILE_PATH)
                except Exception as e:
                    print(f"Warning: Could not create backup file {POSTS_BACKUP_FILE_PATH}: {e}")
                    # Не фатальная ошибка, продолжаем попытку записи в основной файл

        # 3. Добавляем новый пост
        all_posts.append(post_data)

        # 4. Записываем обновленный список обратно в основной файл
        if _write_data_to_file(POSTS_FILE_PATH, all_posts):
            return True
        else:
            print(f"Failed to write new post to {POSTS_FILE_PATH}.")
            return False



def delete_post_by_id(post_id: str) -> bool:

    main_lock = FileLock(POSTS_LOCK_FILE_PATH, timeout=10)
    backup_lock = FileLock(POSTS_BACKUP_LOCK_FILE_PATH, timeout=10)

    with main_lock:
        # 1. Загружаем текущие посты
        all_posts = _read_data_from_file(POSTS_FILE_PATH)
        if all_posts is None:
            print(f"Error: Could not read main posts file {POSTS_FILE_PATH} for deletion.")
            return False

        # 2. Находим пост для удаления
        initial_post_count = len(all_posts)
        # Создаем новый список, исключая пост с заданным ID
        updated_posts = [post for post in all_posts if post.get('id') != post_id]

        if len(updated_posts) == initial_post_count:
            print(f"Post with ID '{post_id}' not found. No changes made.")
            return False  # Пост не найден

        # 3. Делаем резервную копию текущего основного файла, если он существует
        if os.path.exists(POSTS_FILE_PATH) and os.path.getsize(POSTS_FILE_PATH) > 0:
            with backup_lock:
                try:
                    shutil.copyfile(POSTS_FILE_PATH, POSTS_BACKUP_FILE_PATH)
                    print(f"Backup created before deletion: {POSTS_BACKUP_FILE_PATH}")
                except Exception as e:
                    print(f"Warning: Could not create backup before deletion: {e}")

        # 4. Записываем обновленный список обратно в основной файл
        if _write_data_to_file(POSTS_FILE_PATH, updated_posts):
            print(f"Post with ID '{post_id}' successfully deleted.")
            return True
        else:
            print(f"Failed to write updated posts list after deleting post with ID '{post_id}'.")
            return False

