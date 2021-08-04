import telebot
import requests

bot = telebot.TeleBot('1925289738:AAFQOPCVTlknNihpYd44ertOAVnXqvLsD3E')


@bot.message_handler(commands=['start'])
def start_command(message):
    us = message.chat.id
    un = message.chat.username
    res = requests.post(f'http://192.168.0.108:5000/get_tg?username={un}&id={us}').text
    if res == 'nthx':
        bot.send_message(us, 'Вы уже записаны в базу, нет нужды добавлять еще раз')
    elif res == 'thx':
        bot.send_message(us, 'Ваш айди зарегистирован, можно подключать 2FA')


bot.polling()
