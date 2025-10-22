import telebot
from telebot import types
import random
import os

# 🔒 Лучше хранить токен в переменной окружения (а не прямо в коде)
TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")

bot = telebot.TeleBot(TOKEN)

players = []


@bot.message_handler(commands=['start'])
def start(message):
    # Получаем дату из команды /start, например: /start Пятница 25.10
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        date_text = args[1]
    else:
        date_text = "субботу 20.10"  # значение по умолчанию

    markup = types.InlineKeyboardMarkup()
    join_btn = types.InlineKeyboardButton("Играю 🎾", callback_data="join")
    show_btn = types.InlineKeyboardButton("Список 📋", callback_data="show")
    draw_btn = types.InlineKeyboardButton("Рандом 🎲", callback_data="draw")
    markup.add(join_btn, show_btn, draw_btn)

    bot.send_message(
        message.chat.id,
        f"📢 Объявление: Теннис в {date_text}!\nНажмите кнопки, чтобы голосовать за участие.",
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