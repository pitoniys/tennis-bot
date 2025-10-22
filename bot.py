import telebot
from telebot import types
import random
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# === 🔑 Настройки ===
TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# === 📋 Данные ===
players_by_date = {}   # словарь: дата → [игроки]
pending_date = {}      # словарь: user_id → True (ожидаем дату от пользователя)


# === 🚀 Команда /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Напиши дату предстоящей игры (например: Пятница 25.10):"
    )
    pending_date[message.from_user.id] = True  # ожидаем дату от этого пользователя


# === 📅 Получение даты ===
@bot.message_handler(func=lambda m: pending_date.get(m.from_user.id))
def get_date(message):
    date_text = message.text.strip() if message.text else "неизвестная дата"
    pending_date.pop(message.from_user.id, None)  # убираем из ожидания

    # если такой даты ещё нет — создаём запись
    if date_text not in players_by_date:
        players_by_date[date_text] = []

    # создаём кнопки
    markup = types.InlineKeyboardMarkup()
    join_btn = types.InlineKeyboardButton("Играю 🎾", callback_data=f"join|{date_text}")
    show_btn = types.InlineKeyboardButton("Список 📋", callback_data=f"show|{date_text}")
    draw_btn = types.InlineKeyboardButton("Рандом 🎲", callback_data=f"draw|{date_text}")
    markup.add(join_btn, show_btn, draw_btn)

    bot.send_message(
        message.chat.id,
        f"📢 Объявление: Теннис в {date_text}!\n"
        f"Нажмите кнопки, чтобы записаться или посмотреть список игроков.",
        reply_markup=markup
    )


# === 🎾 Обработка кнопок ===
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        action, date_text = call.data.split("|", 1)
    except ValueError:
        bot.answer_callback_query(call.id, "Некорректные данные.")
        return

    user = call.from_user.first_name
    players = players_by_date.setdefault(date_text, [])

    if action == "join":
        if user not in players:
            players.append(user)
            bot.answer_callback_query(call.id, f"{user} записался на {date_text}!")
        else:
            bot.answer_callback_query(call.id, f"{user}, ты уже записан 😉")

    elif action == "show":
        if players:
            bot.send_message(
                call.message.chat.id,
                f"📋 Участники ({date_text}):\n" + "\n".join(players)
            )
        else:
            bot.send_message(call.message.chat.id, f"Пока никто не записался на {date_text}.")

    elif action == "draw":
        if len(players) < 4:
            bot.send_message(call.message.chat.id, f"Мало участников на {date_text}! Нужно хотя бы 4.")
        else:
            selected = random.sample(players, 4)
            bot.send_message(
                call.message.chat.id,
                f"🎾 Сегодня ({date_text}) играют:\n" + "\n".join(selected)
            )


# === 🌐 Мини HTTP-сервер для Render (чтобы бот не засыпал) ===
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"🌐 Web server running on port {port}")
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

# === ▶️ Запуск Telegram-бота ===
print("✅ Bot is running...")
bot.polling(none_stop=True)