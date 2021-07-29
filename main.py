import sqlite3
import nltk

# Data
conn = sqlite3.connect('data.db')
cur = conn.cursor()


def goodtext(text):
    filter = ['а', 'б', ' ', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    ret = ''
    for o in text:
        if o in filter:
            ret += o
    return ret


while True:
    rawtext = input()
    text = goodtext(rawtext)
    cur.execute(f'SELECT * FROM subtitles WHERE text like "%{text}%"')
    results = cur.fetchall()
    print('По вашему запросу найдены следующие варианты:')
    for result in results:
        cur.execute(f'SELECT * FROM films WHERE id = {result[4]}')
        film = cur.fetchone()
        a = f'{film[1]}: {result[0]} --> {result[1]}\n' \
            f'Текст фразы: {result[2]}\n' \
            f'О фильме: {film[2]}\n' \
            f'Рейтинг фильма на Кинопоиске: {film[3]}'
        print('-------------------------------------------------------------')
