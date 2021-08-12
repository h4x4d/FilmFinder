import random
from flask import Flask, render_template, url_for, request, redirect, jsonify
import sqlite3
import hashlib
import datetime
import telebot
from waitress import serve

app = Flask(__name__)
add = []


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
        return redirect(url_for('result', search=request.form['zapros']))
    else:
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
            if res[4]:
                h = res[4].split('; ')
                history = []
                for i in h:
                    i = i.split(': ')
                    history.append(i)
                if history == [['']]:
                    history = None
            else:
                history = None
            return render_template('index.html', history=history)
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
            if request.form['code']:
                c = int(request.form['code'])
                try:
                    cur.execute(f'SELECT * FROM requests WHERE user = "{log}" and code = "{c}" and  name = "login"')
                    if cur.fetchone():
                        ip = request.remote_addr
                        today = datetime.date.today()

                        cur.execute(f'UPDATE users SET session = "{ip}" WHERE login = "{log}"')
                        cur.execute(f'UPDATE users SET sestime = "{str(today)}" WHERE login = "{log}"')
                        cur.execute(f'DELETE FROM requests WHERE user = "{log}";')
                        conn.commit()
                        return jsonify({'login': True})
                    else:
                        return jsonify({'error': 'Неверный код из телеграмма.'})
                except IndexError:
                    return jsonify({'error': 'Неверный код из телеграмма.'})
            ip = request.remote_addr
            today = datetime.date.today()
            try:
                cur.execute(f'SELECT * FROM users WHERE login = "{log}"')
                user = cur.fetchall()[0]
            except IndexError:
                return jsonify({'error': 'Проверьте правильность введенного логина или зарегистрируйтесь.'})

            if user[1] == pas:
                if user[6]:

                    code = random.randint(10000, 99999)
                    bot = telebot.TeleBot('1925289738:AAFQOPCVTlknNihpYd44ertOAVnXqvLsD3E')
                    bot.send_message(user[6], f'Код для входа на сайт: {code}')
                    cur.execute(f'INSERT INTO requests VALUES (?, ?, ?, ?)', ['login', log, code, ''])
                    conn.commit()
                    return jsonify({'code': 'sent'})
                else:
                    cur.execute(f'UPDATE users SET session = "{ip}" WHERE login = "{log}"')
                    cur.execute(f'UPDATE users SET sestime = "{str(today)}" WHERE login = "{log}"')
                    conn.commit()
                    return jsonify({'index': True})
            else:
                return jsonify({'error': 'Проверьте правильность введенного пароля или зарегистрируйтесь.'})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Произошла непридвиденная ошибка. Попробуйте авторизоваться заново.'})
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
        cur.execute('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);', (q['login'], pas, ip, today, '', '', '', None))
        conn.commit()
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
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
            conn = sqlite3.connect('date.db')
            cur = conn.cursor()
            text = request.args.get('search')
            if text:
                text = text.lower()
            else:
                text = ''
            cur.execute(f'SELECT * FROM subtitles WHERE text like "%{text}%"')
            results = cur.fetchall()
            res = []
            for rt in results:
                cur.execute(f'SELECT * FROM films WHERE id = {rt[4]}')
                film = cur.fetchone()

                a = [film[1], rt[0], rt[1], rt[2], film[2], None, str(film[0])]

                res.append(a)
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            ip = request.remote_addr
            cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
            newhist = cur.fetchall()[0]
            cur.execute(f'SELECT * FROM liked WHERE userId = "{newhist[7]}"')
            like = cur.fetchone()
            if not like:
                like = []
            else:
                like = like[2].split('; ')
            if newhist[4]:
                newhist = newhist[4] + f'; {text}: {len(results)}'
            else:
                newhist = f'{text}: {len(results)}'
            cur.execute(f'SELECT * FROM liked WHERE userId = "{ip}"')
            cur.execute(f'UPDATE users SET history = "{newhist}" WHERE session = "{ip}"')
            conn.commit()

            return render_template('result.html', result=res, like=like)
        else:
            return redirect(url_for('login', error=4))

    else:
        usid = request.form['id']
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        ip = request.remote_addr
        cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
        res = cur.fetchone()
        us = res[7]
        cur.execute(f'SELECT * FROM liked WHERE userId = "{us}"')
        res = cur.fetchone()
        if not res:
            cur.execute(f'INSERT INTO liked VALUES(?, ?, ?)', (None, us, f'{usid}'))
            conn.commit()
            return jsonify({'send': '1'})
        elif not res[2]:
            cur.execute(f'UPDATE liked SET filmIds = "{usid}" WHERE userId = "{us}"')
            conn.commit()
            return jsonify({'send': '1'})
        else:
            if usid not in res[2].split('; '):
                cur.execute(f'UPDATE liked SET filmIds = "{res[2] + "; " + usid}" WHERE userId = "{us}"')
                conn.commit()
                return jsonify({'send': '1'})
            else:
                films = res[2].split('; ')
                films.remove(usid)
                films = '; '.join(films)
                cur.execute(f'UPDATE liked SET filmIds = "{films}" WHERE userId = "{us}"')
                conn.commit()
                return jsonify({'notsend': '1'})


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
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
            if res[6]:
                return render_template('profile.html', tg=res[6])
            else:
                return render_template('profile.html', tg=0)
        else:
            return redirect(url_for('login', error=4))

    else:
        pass


@app.route('/get_tg', methods=['POST'])
def get_tg():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    us = request.args.get('username')
    un = request.args.get('id')
    try:
        cur.execute('INSERT INTO tg VALUES(?, ?);', (un, us.lower()))
    except sqlite3.IntegrityError:
        return 'nthx'
    conn.commit()
    return 'thx'


@app.route('/process', methods=['POST'])
def process():
    try:
        us = request.form['username']
        pas = shifr(request.form['pass'])
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        ip = request.remote_addr
        cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
        user = cur.fetchone()

        if user[1] == pas:
            try:
                bot = telebot.TeleBot('1925289738:AAFQOPCVTlknNihpYd44ertOAVnXqvLsD3E')
                cur.execute(f'SELECT * FROM tg WHERE username = "{us}"')

                tg = cur.fetchone()
                bot.send_message(tg[0], f'Проверочная ссылка, для подтверждения 2FA Доступа: '
                                        f'https://film-from-text.herokuapp.com/confirm?id={pas}&tg={tg[0]}')
                return jsonify({'send': True})
            except TypeError:
                return jsonify({'error': 'Вы не отправляли сообщения нашему боту.'})
        else:
            return jsonify({'error': 'Неверно введен пароль'})
    except IndexError:
        return jsonify({'error': 'Произошла непредвиденная ошибка. Попробуйте войти еще раз'})


@app.route('/confirm')
def confirm():
    id_pass = request.args.get('id')
    tg = request.args.get('tg')
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET tgid = "{tg}" WHERE password = "{id_pass}"')
    conn.commit()
    return render_template('confirm.html')


@app.route('/liked')
def liked():
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
        cur.execute(f'SELECT * FROM liked WHERE userId = "{res[7]}"')
        likes = cur.fetchone()
        if not likes:
            return render_template('liked.html', result=None, like=[])
        else:
            likes = likes[2].split('; ')
            conn = sqlite3.connect('date.db')
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM films WHERE id in ({", ".join(likes)})')
            ld = cur.fetchall()
            for j, i in enumerate(ld):
                ld[j] = [str(i[0]), i[1], i[2]]
            return render_template('liked.html', result=ld, like=likes)
    else:
        return redirect(url_for('login', error=4))


@app.route('/passchange', methods=["POST"])
def passchange():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    newp = shifr(request.form['pass'])
    oldp = shifr(request.form['oldpass'])
    if request.form['code']:
        try:
            code = request.form['code']
            cur.execute(f'SELECT * FROM requests WHERE code = "{code}" AND other = "{newp}"')
            if cur.fetchone():
                cur.execute(f'UPDATE users SET password = "{newp}" WHERE password = "{oldp}"')
                cur.execute(f'DELETE FROM requests WHERE other = "{newp}";')
                conn.commit()
                return jsonify({'success': 'Пароль успешно сменен!'})
            else:
                return jsonify({'error': 'Введенный код неверен!'})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Введенный код неверен!'})

    else:
        newp2 = shifr(request.form['pass_2'])
        another = request.form['pass_2']
        cur.execute(f'SELECT * FROM users WHERE password = "{oldp}"')
        us = cur.fetchone()
        num = random.randint(10000, 99999)
        if us:
            if newp == newp2 and len(another) > 7:
                if us[6]:
                    bot = telebot.TeleBot('1925289738:AAFQOPCVTlknNihpYd44ertOAVnXqvLsD3E')
                    bot.send_message(us[6], f'Проверочный код для смены пароля: {num}')
                    cur.execute(f'INSERT INTO requests VALUES(?, ?, ?, ?)', ['changepass', us[0], num, newp])
                    conn.commit()
                    return jsonify({'alert': 'В ваш телеграм отправлен проверочный код'})
                else:
                    cur.execute(f'UPDATE users SET password = "{newp}" WHERE password = "{oldp}"')
                    conn.commit()
                    return jsonify({'success': 'Пароль успешно сменен!'})
            else:
                return jsonify({'error': 'Пароли не совпадают или длина пароля недостаточна.'})
        else:
            return jsonify({'error': 'Неверный старый пароль'})


@app.route('/offtg', methods=['POST', 'GET'])
def offtg():
    ip = request.remote_addr
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET tgid = "" WHERE session = "{ip}"')
    conn.commit()
    return redirect(url_for('profile'))


@app.route('/profile_act', methods=['POST'])
def setting():
    t = request.form['type']
    if t == 'clearhistory':
        ip = request.remote_addr
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET history = "" WHERE session = "{ip}"')
        conn.commit()
        return jsonify({'delete': 'История поиска очищена'})
    if t == 'clearliked':
        ip = request.remote_addr
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM users WHERE session = "{ip}"')
        s = cur.fetchone()
        cur.execute(f'UPDATE liked SET FilmIds = "" WHERE userId = "{s[7]}"')
        conn.commit()
        return jsonify({'delete': 'Ваши понравившиеся очищены'})
    if t == 'exit':
        ip = request.remote_addr
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET session = "" WHERE session = "{ip}"')
        conn.commit()
        return jsonify({'delete': 'Выход успешен'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
