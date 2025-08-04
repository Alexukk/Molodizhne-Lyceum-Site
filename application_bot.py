from telebot import types, TeleBot
import dotenv
import os
import logging
import time

dotenv.load_dotenv()
bot = TeleBot(os.getenv("BOT_APPLICATION_KEY"))
chat_id = os.getenv("ADMINS_CHAT_ID")

messages = {}

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(types.KeyboardButton('Залишити повідомлення'))
menu.add(types.KeyboardButton("Про бота"))

def show_menu(message):
    bot.send_message(message.chat.id, 'Повертаю у меню', reply_markup=menu)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    show_menu(message)

@bot.message_handler(commands=['start'])
def start(message):
    id = message.chat.id
    bot.send_message(
        id,
        f"Вітаю {message.from_user.first_name}, цей бот створено для зв'язку з адміністрацією ліцею. "
        f"Виберіть одну з опцій нижче для роботи з ботом",
        reply_markup=menu
    )

@bot.message_handler(func=lambda m: m.text == 'Про бота')
def about(message):
    id = message.chat.id
    bot.send_message(id, "Цей бот створенний для легкого зв'язку з адміністрацією Молодіжненського ліцею\n"
                         "Щоб надіслати ваше повідомлення/пропозицію натисніть кнопку 'Залишити повідомлення' у меню нижче.\n")

@bot.message_handler(func=lambda m: m.text == 'Залишити повідомлення')
def send_message(message):
    id = message.chat.id
    msg = bot.send_message(
        id,
        "Надішліть ваше повідомлення адміністрації одним текстом або натисніть /menu щоб повернутися.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, message_getter)

def message_getter(message):
    user_id = message.chat.id
    text = message.text

    if text.strip().lower() == '/menu':
        show_menu(message)
        return

    messages[user_id] = {'text': text}

    bot.send_message(user_id, 'Перевірте свій текст:')
    bot.send_message(user_id, text)
    bot.send_message(user_id, "Введіть 'так' щоб підтвердити або 'ні' щоб переписати")
    bot.register_next_step_handler(message, message_checker)

def message_checker(message):
    user_id = message.chat.id
    ans = message.text.strip().lower()

    if ans == '/menu':
        show_menu(message)
        return

    if ans == 'так':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        contact_btn = types.KeyboardButton("📱 Надіслати контакт", request_contact=True)
        kb.add(contact_btn)
        bot.send_message(user_id, "Надішліть свій контакт для зворотного зв’язку:", reply_markup=kb)
        bot.register_next_step_handler(message, contact_getter)

    elif ans == 'ні':
        bot.send_message(user_id, 'Спробуйте ще раз')
        send_message(message)

    else:
        bot.send_message(user_id, "Нема такого варіанту відповіді, спробуйте ще раз")
        bot.register_next_step_handler(message, message_checker)

def contact_getter(message):
    user_id = message.chat.id
    if message.contact:
        contact = message.contact.phone_number
        messages[user_id]['contact'] = contact

        full_message = (
            f"🚨 НОВЕ ЗВЕРНЕННЯ 🚨\n"
            f"👤 Ім'я: {message.from_user.first_name} {message.from_user.last_name or ''}\n"
            f"🔗 Username: @{message.from_user.username or '—'}\n"
            f"📞 Контакт: {contact}\n"
            f"✉️ Звернення:\n{messages[user_id]['text']}"
        )

        bot.send_message(chat_id, full_message)
        bot.send_message(user_id, "Ваше звернення надіслано ✅", reply_markup=menu)

    else:
        bot.send_message(user_id, "Контакт не отримано. Будь ласка, спробуйте ще раз.")
        bot.register_next_step_handler(message, contact_getter)

def start_application_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logging.exception("❌ Бот упав з помилкою:")
            time.sleep(5)
