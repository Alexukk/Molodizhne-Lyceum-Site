import json
import time
import telebot
import os
import dotenv
import datetime
import requests
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
dotenv.load_dotenv()

# Инициализация бота с токеном из переменной окружения
bot = telebot.TeleBot(os.getenv("BOT_KEY"))

# Получение ID администраторов из переменных окружения
ADMIN_ID_STR = os.getenv('ADMIN_ID')
DEV_ID_STR = os.getenv('DEV_ID')

# Проверка, что переменные окружения установлены
if ADMIN_ID_STR is None or DEV_ID_STR is None:
    logger.critical("ADMIN_ID or DEV_ID environment variables are not set. Exiting.")
    raise ValueError("ADMIN_ID or DEV_ID environment variables are not set.")

# Преобразование ID администраторов в целые числа
admins = [int(ADMIN_ID_STR), int(DEV_ID_STR)]
logger.info(f"Admin IDs loaded: {admins}")

# Глобальная переменная для хранения данных текущего поста.
Post = {}

# Создание главного меню (ReplyKeyboardMarkup)
menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('/AddPost')
btn3 = types.KeyboardButton('/DeletePost')
btn5 = types.KeyboardButton('/ChangeSchedule')
btn6 = types.KeyboardButton('/Instruction')
menu.add(btn1, btn3, btn5, btn6)

# Объект для скрытия клавиатуры
hide_menu = types.ReplyKeyboardRemove()

# Меню для удаления постов
delete_management_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
delete_management_menu.add(types.KeyboardButton('Exit'))
delete_management_menu.add(types.KeyboardButton('DELETE_POST'))


def checker(user_id):
    if user_id not in admins:
        logger.warning(f"Unauthorized access attempt by user ID: {user_id}")
        bot.send_message(user_id, "Ви не маєте доступу до цього боту.", reply_markup=hide_menu)
        return False
    return True


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    logger.info(f"User {user_id} started bot.")
    if not checker(user_id):
        return
    bot.send_message(user_id,
                     "Цей бот створений для керування сайтом ліцею,\n "
                     "для ознайомлення з ботом натисніть кнопку /Instruction",
                     reply_markup=menu)


@bot.message_handler(commands=['Instruction'])
def Instruction(message):
    user_id = message.chat.id
    logger.info(f"User {user_id} requested instructions.")
    if not checker(user_id):
        return
    text = "Тут буде інструкція по використанню:\n" \
           "/AddPost - додати новий пост на сайт.\n" \
           "/DeletePost - видалити пост.\n" \
           "/ChangeSchedule - змінити розклад.\n"
    bot.send_message(user_id, text, reply_markup=menu)


@bot.message_handler(commands=['AddPost'])
def AddPost(message):
    user_id = message.chat.id
    logger.info(f"User {user_id} initiated AddPost process.")
    if not checker(user_id):
        return

    global Post
    Post = {}

    bot.send_message(user_id, "Введіть заголовок поста:", reply_markup=hide_menu)
    bot.register_next_step_handler(message, get_text_post)


def get_text_post(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    global Post
    Post['title'] = message.text
    Post['id'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    Post['Date'] = datetime.datetime.now().strftime("%H:%M %d %B %Y")

    bot.send_message(user_id, "Введіть текст поста (Одним повідомленням)")
    bot.register_next_step_handler(message, verifying_post)


def verifying_post(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    global Post
    confirm_post_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    confirm_post_menu.add(types.KeyboardButton('Publish-Post'))
    confirm_post_menu.add(types.KeyboardButton('Exit'))

    Post['text'] = message.text

    bot.send_message(user_id, 'Перевірте пост:', reply_markup=confirm_post_menu)
    bot.send_message(user_id, f"Заголовок: {Post['title']}\n"
                              f"Текст: {Post['text']}\n"
                              f"----------------------| {Post['Date']}\n"
                              f"ID: <code>{Post['id']}</code>",
                     reply_markup=confirm_post_menu,
                     parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == 'Publish-Post')
def PublishPost(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    global Post

    if not Post or 'title' not in Post or 'text' not in Post or 'id' not in Post:
        bot.send_message(user_id, "Немає поста для публікації. Спробуйте /AddPost знову.", reply_markup=menu)
        return

    try:
        data = {
            'title': Post['title'],
            'id': Post['id'],
            'text': Post['text'],
            'Date': Post['Date']
        }

        path = os.path.join(os.path.dirname(__file__), "posts_for_bot.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding='utf8') as file:
                    posts = json.load(file)
            else:
                posts = []
        except Exception:
            posts = []

        posts.append(data)

        with open(path, "w", encoding='utf8') as file:
            json.dump(posts, file, ensure_ascii=False, indent=2)

        response = requests.post(
            'https://molodizhne-lyceum-site.onrender.com/update-posts',
            json=Post,
            timeout=30
        )
        if response.status_code == 200:
            bot.send_message(user_id, "✅ Пост успішно опубліковано!", reply_markup=menu)
            Post = {}
        else:
            bot.send_message(user_id, f"❌ Помилка: сервер відповів {response.status_code}", reply_markup=menu)
    except Exception as e:
        bot.send_message(user_id, f"⚠️ Помилка при надсиланні поста: {e}\n Спробуйте знову через 30 секунд, сервер прокидається", reply_markup=menu)


@bot.message_handler(commands=['DeletePost'])
def show_posts_for_deletion(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    bot.send_message(user_id, "Введіть ID поста, який ви хочете видалити:", reply_markup=delete_management_menu)
    bot.register_next_step_handler(message, posts_deleter)


@bot.message_handler(commands=['AllPosts'])
def all_posts(message):
    user_id = message.chat.id
    try:
        with open("posts_for_bot.json", "r", encoding="utf8") as f:
            posts = json.load(f)
        if not posts:
            bot.send_message(user_id, "Пости відсутні.", reply_markup=menu)
            return
    except Exception as e:
        bot.send_message(user_id, f"Помилка читання постів: {e}", reply_markup=menu)
        return

    for post in posts:
        text = (
            f"<b>{post.get('title', 'Без назви')}</b>\n"
            f"{post.get('text', '')}\n"
            f"{post.get('Date', '')}\n"
            f"<code>{post.get('id', '')}</code>"
        )
        bot.send_message(user_id, text, parse_mode='HTML')




@bot.message_handler(commands=['DeletePost'])
def delete_post_command(message):
    user_id = message.chat.id
    if not checker(user_id):
        return
    try:
        with open("posts_for_bot.json", "r", encoding="utf8") as f:
            posts = json.load(f)
        if not posts:
            bot.send_message(user_id, "Пости відсутні.", reply_markup=menu)
            return
    except Exception as e:
        bot.send_message(user_id, f"Помилка читання постів: {e}", reply_markup=menu)
        return
    global text
    for post in posts:
        text = (
            f"<b>{post.get('title', 'Без назви')}</b>\n"
            f"{post.get('text', '')}\n"
            f"{post.get('Date', '')}\n"
            f"<code>{post.get('id', '')}</code>"
        )
    bot.send_message(user_id, text, parse_mode='HTML')

    bot.send_message(user_id, f"Введіть ID поста для видалення: {text}", reply_markup=delete_management_menu)
    bot.register_next_step_handler(message, posts_deleter)



def posts_deleter(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    if message.text == 'Exit':
        bot.send_message(user_id, "Видалення постів скасовано.", reply_markup=menu)
        return

    post_id_to_delete = message.text.strip()

    try:
        response = requests.post(
            'https://molodizhne-lyceum-site.onrender.com/update-posts',
            json={"title": "DELETE", "id": post_id_to_delete},
            timeout=10
        )
        if response.status_code == 200:
            path = os.path.join(os.path.dirname(__file__), "posts_for_bot.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                # Фильтруем посты, убирая удалённый
                data = [post for post in data if post.get("id") != post_id_to_delete]
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)

            bot.send_message(
                user_id,
                f"✅ Пост з ID <code>{post_id_to_delete}</code> успішно видалено.",
                reply_markup=menu,
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                user_id,
                f"❌ Сервер не зміг видалити пост з ID <code>{post_id_to_delete}</code>.",
                reply_markup=menu,
                parse_mode='HTML'
            )
            bot.register_next_step_handler(message, posts_deleter)
    except Exception as e:
        bot.send_message(
            user_id,
            f"⚠️ Помилка при спробі видалення поста: {e}",
            reply_markup=menu
        )
        bot.register_next_step_handler(message, posts_deleter)



@bot.message_handler(func=lambda message: message.text == 'Exit')
def Exit(message):
    user_id = message.chat.id
    if not checker(user_id):
        return

    global Post
    Post = {}

    bot.send_message(user_id, "Повертаю у меню.", reply_markup=menu)


def start_admin_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logging.exception("❌ Бот упал с ошибкой:")
            time.sleep(5)


if __name__ == '__main__':
    logger.info("Bot started polling...")
    start_admin_bot()
