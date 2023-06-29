import os

from flask import Flask, request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import random
import telebot

TOKEN = '5860394201:AAGa7Vk6n1Xn_gead9O-zeEHkGdOcSdsj4g'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
number = None
scores = {}
guesses = 5
game_over = False

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text="سلام! به بازی حدس عدد خوش آمدید. من یک عدد بین ۱ تا ۱۰۰ انتخاب کرده‌ام. شما باید حدس بزنید که عدد چیست.")

@bot.message_handler(commands=['score'])
def view_scores(message):
    top_users = sorted(scores, key=scores.get, reverse=True)[:5]
    score_list = "\n".join([f"{i + 1}. {top_users[i]}: {scores[top_users[i]]}" for i in range(len(top_users))])
    message.bot.send_message(chat_id=message.effective_chat.id, text=f"امتیازها:\n{score_list}")

@bot.message_handler(func=lambda message: True)
def guess(message):
    global scores, guesses, game_over
    if game_over:
        message.bot.send_message(chat_id=message.effective_chat.id,
                                 text="بازی به پایان رسید. برای شروع دوباره /start را وارد کنید.")
        return
    try:
        user_number = int(message.message.text)
        if user_number == number:
            message.bot.send_message(chat_id=message.effective_chat.id, text="تبریک! شما عدد را درست حدس زدید.")
            if message.message.chat.username not in scores:
                scores[message.message.chat.username] = 0
            scores[message.message.chat.username] += 1
            game_over = True
        elif user_number < message:
            message.bot.send_message(chat_id=message.effective_chat.id, text="عدد من بیشتر است.")
        elif user_number > message:
            message.bot.send_message(chat_id=message.effective_chat.id, text="عدد من کمتر است.")
        guesses -= 1
        if guesses == 0:
            message.bot.send_message(chat_id=message.effective_chat.id,
                                     text=f"شما نتوانستید عدد را حدس بزنید! عدد من {number} بود. برای شروع دوباره /start را وارد کنید.")
            game_over = True
    except ValueError:
        message.bot.send_message(chat_id=message.effective_chat.id, text="لطفا یک عدد صحیح بین ۱ تا ۱۰۰ وارد کنید.")

def main():
    global bot
    bot = Updater(token=TOKEN, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("score", view_scores))
    dp.add_handler(MessageHandler(Filters.text, guess))
    bot.start_polling()
    bot.idle()

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://gamenumberbot.42web.io/' + TOKEN)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
