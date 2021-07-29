from flask import Flask, render_template, url_for, request, redirect
import sqlite3


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        text = request.form['fraze']
        cur.execute(f'SELECT * FROM subtitles WHERE text like "%{text}%"')
        results = cur.fetchall()
        res = []
        for result in results:
            cur.execute(f'SELECT * FROM films WHERE id = {result[4]}')
            film = cur.fetchone()
            a = [film[1], result[0], result[1], result[2], film[2], film[3]]
            """a = f'{film[1]}: {result[0]} --> {result[1]}<p>' \
                f'Текст фразы: {result[2]}<p>' \
                f'О фильме: {film[2]}<p>' \
                f'Рейтинг фильма на Кинопоиске: {film[3]}'"""
            res.append(a)
        return render_template('result.html', result=res, num=1)
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


app.run(debug=True)