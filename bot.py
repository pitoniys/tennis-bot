import telebot
from telebot import types
import random
import os

TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

players = []
pending_date = {}  # словарь: user_id → ждём дату


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Напиши дату предстоящей игры (например: Пятница 25.10):")
    pending_date[message.chat.id] = True  # отмечаем, что ждём дату


@bot.message_handler(func=lambda m: m.chat.id in pending_date)
def get_date(message):
    date_text = message.text.strip()
    del pending_date[message.chat.id]  # больше не ждём

    markup = types.InlineKeyboardMarkup()
    join_btn = types.InlineKeyboardButton("Играю 🎾", callback_data="join")
    show_btn = types.InlineKeyboardButton("Список 📋", callback_data="show")
    draw_btn = types.InlineKeyboardButton("Рандом 🎲", callback_data="draw")
    markup.add(join_btn, show_btn, draw_btn)

    bot.send_message(
        message.chat.id,
        f"📢 Объявление: Теннис в {date_text}!\nНажмите кнопки, чтобы записаться или посмотреть список.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user = call.from_user.first_name
    if call.data == "join":
        if user not in players:
            players.append(user)
            bot.answer_callback_query(call.id, f"{user} присоединился!")
        else:
            bot.answer_callback_query(call.id, f"{user}, ты уже в списке 😉")

    elif call.data == "show":
        if players:
            bot.send_message(call.message.chat.id, "Список участников:\n" + "\n".join(players))
        else:
            bot.send_message(call.message.chat.id, "Пока никто не присоединился.")

    elif call.data == "draw":
        if len(players) < 4:
            bot.send_message(call.message.chat.id, "Мало участников! Нужно хотя бы 4.")
        else:
            selected = random.sample(players, 4)
            bot.send_message(call.message.chat.id, "🎾 Сегодня играют:\n" + "\n".join(selected))


print("✅ Bot is running...")
bot.polling(none_stop=True)