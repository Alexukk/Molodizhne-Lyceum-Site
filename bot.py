import time
import telebot
import os
import dotenv
import datetime
from telebot import types
import logging

# Импортируем все необходимые функции из вашего json_storage.py
from json_storage import load_posts, save_post, delete_post_by_id
from scedule_updater import scedule_updater

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

# Создание объекта для скрытия Reply-клавиатуры
hide_menu = types.ReplyKeyboardRemove()

# Клавиатура для режима удаления (с кнопками "Exit" и "DELETE_POST")
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
    """Обработчик команды /start."""
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
    """Обработчик команды /Instruction."""
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
    """Начинает процесс добавления нового поста."""
    user_id = message.chat.id
    logger.info(f"User {user_id} initiated AddPost process.")
    if not checker(user_id):
        return

    global Post
    Post = {}

    bot.send_message(user_id, "Введіть заголовок поста:", reply_markup=hide_menu)
    bot.register_next_step_handler(message, get_text_post)


def get_text_post(message):
    """Получает заголовок поста и запрашивает текст."""
    user_id = message.chat.id
    logger.info(f"User {user_id} provided post title.")
    if not checker(user_id):
        return

    global Post
    Post['title'] = message.text
    Post['id'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    Post['Date'] = datetime.datetime.now().strftime("%H:%M %d %B %Y")

    bot.send_message(user_id, "Введіть текст поста (Одним повідомленням)")
    bot.register_next_step_handler(message, verifying_post)


def verifying_post(message):
    """Получает текст поста, показывает его для проверки и предлагает действия."""
    user_id = message.chat.id
    logger.info(f"User {user_id} provided post text for verification.")
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
    """Обрабатывает публикацию поста."""
    user_id = message.chat.id
    logger.info(f"User {user_id} attempting to publish post.")
    if not checker(user_id):
        return

    global Post

    if not Post or 'title' not in Post or 'text' not in Post or 'id' not in Post:
        logger.warning(f"User {user_id} tried to publish empty/incomplete post.")
        bot.send_message(user_id, "Немає поста для публікації. Спробуйте /AddPost знову.", reply_markup=menu)
        return

    if save_post(Post):
        logger.info(f"Post ID {Post['id']} successfully published by user {user_id}.")
        bot.send_message(user_id, "Пост успішно опубліковано!", reply_markup=menu)
        Post = {}
    else:
        logger.error(f"Failed to publish post by user {user_id}. Post data: {Post}")
        bot.send_message(user_id, "Помилка при публікації поста. Спробуйте знову.", reply_markup=menu)


@bot.message_handler(commands=['DeletePost'])
def show_posts_for_deletion(message):
    """Показывает список постов для выбора ID для удаления."""
    user_id = message.chat.id
    logger.info(f"User {user_id} initiated DeletePost process.")
    if not checker(user_id):
        return

    posts = load_posts()
    if not posts:
        logger.info(f"No posts found for deletion for user {user_id}.")
        bot.send_message(user_id, "Наразі немає постів для видалення.", reply_markup=menu)
        return

    bot.send_message(user_id, "Оберіть пост для видалення (натисніть на його ID, щоб скопіювати):",
                     reply_markup=hide_menu)

    for post in posts:
        post_id = post.get('id')
        if not post_id:
            logger.warning(f"Found a post without an ID: {post.get('title', 'N/A')}")
            continue
        bot.send_message(
            user_id,
            f"Заголовок: {post.get('title', 'Без заголовка')}\n"
            f"Дата: {post.get('Date', 'Не вказано')}\n"
            f"ID: <code>{post_id}</code>\n"
            f"Текст: {post.get('text', 'Без тексту')[:70]}...",
            parse_mode='HTML'
        )

    bot.send_message(user_id, "Коли закінчите перегляд, оберіть одну з опцій у меню нижче:",
                     reply_markup=delete_management_menu)


@bot.message_handler(func=lambda message: message.text == 'DELETE_POST')
def DELETE_POST_command_handler(message):
    user_id = message.chat.id
    logger.info(f"User {user_id} chose to delete a post via DELETE_POST button.")
    if not checker(user_id):
        return

    bot.send_message(user_id, "Введіть ID поста для видалення:", reply_markup=delete_management_menu)
    bot.register_next_step_handler(message, posts_deleter)


def posts_deleter(message):
    """Получает ID поста от пользователя и пытается его удалить."""
    user_id = message.chat.id
    logger.info(f"User {user_id} submitted text for post deletion: '{message.text}'")
    if not checker(user_id):
        return

    if message.text == 'Exit':
        logger.info(f"User {user_id} cancelled post deletion.")
        bot.send_message(user_id, "Видалення постів скасовано.", reply_markup=menu)
        return

    post_id_to_delete = message.text.strip()
    logger.info(f"Attempting to delete post with ID: '{post_id_to_delete}' for user {user_id}.")

    result = delete_post_by_id(post_id_to_delete)

    if result:
        logger.info(f"Post ID '{post_id_to_delete}' successfully deleted for user {user_id}.")
        bot.send_message(user_id, f"Пост з ID: <code>{post_id_to_delete}</code> видалено успішно.",
                         reply_markup=menu, parse_mode='HTML')
    else:
        logger.warning(
            f"Failed to delete post ID '{post_id_to_delete}' for user {user_id}. Post not found or error occurred.")
        bot.send_message(user_id, f"Не вдалося видалити пост з ID: <code>{post_id_to_delete}</code>. "
                                  f"Можливо, такий ID не знайдено або сталася помилка. Спробуйте ще раз, "
                                  f"ввівши ID або натисніть 'Exit'.",
                         reply_markup=delete_management_menu, parse_mode='HTML')
        bot.register_next_step_handler(message, posts_deleter)


@bot.message_handler(func=lambda message: message.text == 'Exit')
def Exit(message):
    """Обрабатывает команду 'Exit' для отмены текущего действия и возврата в меню."""
    user_id = message.chat.id
    logger.info(f"User {user_id} activated 'Exit' command/button.")
    if not checker(user_id):
        return

    global Post
    Post = {}

    bot.send_message(user_id, "Повертаю у меню.", reply_markup=menu)

@bot.message_handler(commands=['ChangeSchedule'])
def change_schedule(message):
    if not checker(message.chat.id):
        return
    mrk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mrk.add(types.KeyboardButton('Elementary'))
    mrk.add(types.KeyboardButton('Secondary'))
    mrk.add(types.KeyboardButton('High'))
    mrk.add(types.KeyboardButton('Exit'))

    bot.send_message(message.chat.id, f"Оберіть одну з опцій нижче де \n"
                                      f"Elementary - початкова школа\n"
                                      f"Secondary - середня школа\n"
                                      f"High - старша школа", reply_markup=mrk)


@bot.message_handler(func=lambda message: message.text == 'Elementary')
def elementary(message):
    if not checker(message.chat.id):
        return

    bot.send_message(message.chat.id, 'Надішліть нове посилання на розклад для початкових класів', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, confirm_elementary)


def confirm_elementary(message):
    text = scedule_updater(message.text, 'Elementary')
    bot.send_message(message.chat.id, text, reply_markup=menu)


@bot.message_handler(func=lambda message: message.text == 'Secondary')
def secondary(message):
    if not checker(message.chat.id):
        return

    bot.send_message(message.chat.id, 'Надішліть нове посилання на розклад для середніх класів', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, confirm_secondary)


def confirm_secondary(message):
    text = scedule_updater(message.text, 'Secondary')
    bot.send_message(message.chat.id, text, reply_markup=menu)


@bot.message_handler(func=lambda message: message.text == 'High')
def high(message):
    if not checker(message.chat.id):
        return

    bot.send_message(message.chat.id, 'Надішліть нове посилання на розклад для старших класів', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, confirm_high)


def confirm_high(message):
    text = scedule_updater(message.text, 'High')
    bot.send_message(message.chat.id, text, reply_markup=menu)


if __name__ == '__main__':
    logger.info("Bot started polling...")
    bot.polling(none_stop=True)