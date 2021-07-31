import random

from flask import Flask, render_template, url_for, request, redirect
import sqlite3
import hashlib
import datetime
app = Flask(__name__)


def shifr(message, check=False):
    message = hashlib.sha256(message.encode()).hexdigest()
    if check:
        if message == check:
            return True
        else:
            return False
    else:
        return message


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
        device = request.headers.get('User-Agent').lower().find('android')
        if device != -1:
            pass
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        ip = request.remote_addr
        a = datetime.date.today()
        try:
            cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
            res = cur.fetchall()[0]
        except IndexError:
            return redirect(url_for('login', error=3))
        ses = [int(i) for i in str(res[3]).split('-')]
        ses = datetime.date(ses[0], ses[1], ses[2])
        if (a - ses).days == 0:
            return render_template('index.html')
        else:
            return redirect(url_for('login', error=4))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            log = request.form['login']
            pas = shifr(request.form['password'])
            ip = request.remote_addr
            today = datetime.date.today()
            try:
                cur.execute(f'SELECT * FROM users WHERE login = "{log}"')
                user = cur.fetchall()[0]
            except IndexError:
                return render_template('login.html', error=1)

            if user[1] == pas:
                cur.execute(f'UPDATE users SET session = "{ip}" WHERE login = "{log}"')
                cur.execute(f'UPDATE users SET sestime = "{str(today)}" WHERE login = "{log}"')
                conn.commit()
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error=2)
        except Exception as e:
            return str(e)
    else:
        err = request.args.get('error')
        if err:
            err = int(err)
            return render_template('login.html', error=err)
        return render_template('login.html', error=0)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        ip = request.remote_addr
        q = request.form
        cur.execute(f'SELECT * FROM users WHERE login = "{q["login"]}"')
        user = cur.fetchall()
        cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
        res = cur.fetchall()
        if res:
            return render_template('register.html', error=4)
        if user:
            return render_template('register.html', error=1)
        elif len(q['password']) < 8:
            return render_template('register.html', error=2)
        elif q['password'] != q['password-2']:
            return render_template('register.html', error=3)
        today = datetime.date.today()

        pas = shifr(q['password'])
        a = random.getrandbits(64)
        cur.execute('INSERT INTO users VALUES(?, ?, ?, ?);', (q['login'], pas, ip, today))
        conn.commit()
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


app.run(debug=True, host='0.0.0.0')