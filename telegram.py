import telebot
import sqlite3


bot = telebot.TeleBot('1925289738:AAFQOPCVTlknNihpYd44ertOAVnXqvLsD3E')


@bot.message_handler(commands=['start'])
def start_command(message):
    us = message.chat.id
    un = message.chat.username

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    try:
        cur.execute(f'SELECT * FROM tg WHERE id = "{us}"')
        a = cur.fetchall()[0]
        bot.send_message(us, 'Вы уже записаны')
    except IndexError:
        cur.execute('INSERT INTO tg VALUES(?, ?);', (un.lower(), us))
        bot.send_message(us, 'Вы добавлены в базу')
        conn.commit()




bot.polling()
