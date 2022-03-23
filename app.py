import random
from pymorphy2 import MorphAnalyzer
from flask import Flask, render_template, url_for, request, \
    redirect, jsonify, make_response
import sqlite3
import hashlib
import datetime
import telebot
from spellchecker import SpellChecker
from string import ascii_lowercase, ascii_letters

asc = ascii_lowercase + ascii_letters

token = ''
app = Flask(__name__)
app.debug = True

bot = telebot.TeleBot(token)

spell = SpellChecker(language='ru')
morph = MorphAnalyzer()

users_base = sqlite3.connect('users.db', check_same_thread=False)
users_cur = users_base.cursor()

conn = sqlite3.connect('date.db', check_same_thread=False)
cur = conn.cursor()


def sha_password(message, check=False):
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
        if request.form['if_logged'] == 'True':
            if request.form['submit_btn'] == 'std':
                return redirect(url_for('result_no_login',
                                        search=request.form['zapros'],
                                        search_type=0,
                                        page=1))
            elif request.form['submit_btn'] == 'half':
                return redirect(url_for('result_no_login',
                                        search=request.form['zapros'],
                                        search_type=2,
                                        page=1))
            else:
                return redirect(url_for('result_no_login',
                                        search=request.form['zapros'],
                                        search_type=1,
                                        page=1))
        if request.form['submit_btn'] == 'std':
            return redirect(url_for('result',
                                    search=request.form['zapros'],
                                    search_type=0,
                                    page=1))
        elif request.form['submit_btn'] == 'half':
            return redirect(url_for('result',
                                    search=request.form['zapros'],
                                    search_type=2,
                                    page=1))
        else:
            return redirect(url_for('result',
                                    search=request.form['zapros'],
                                    search_type=1,
                                    page=1))
    else:
        cookie_session = request.cookies.get('token_session')
        if cookie_session:

            try:
                user = users_cur.execute('SELECT * FROM sessions '
                                         'WHERE session = ?',
                                         (cookie_session,)).fetchone()
                user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                                         (user[0],)).fetchone()
                _ = user[0]
            except TypeError:
                return render_template('index-nologin.html')

            if not user:
                return '123'

            if user[4]:
                h = user[4].split('; ')
                history = []
                for i in h:
                    i = i.split(': ')
                    history.append(i)
                history.reverse()
                if history == [['']]:
                    history = None
            else:
                history = None
            return render_template('index.html', history=history)

        else:
            return render_template('index-nologin.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        log = request.form['login']
        pas = sha_password(request.form['password'])

        if request.form['code']:
            c = int(request.form['code'])
            try:
                users_cur.execute(f'SELECT * FROM requests WHERE '
                                  f'user = "{log}" and '
                                  f'code = "{c}" and  name = "login"')
                if users_cur.fetchone():
                    ip = request.remote_addr
                    today = datetime.date.today()

                    users_cur.execute(
                        f'UPDATE users SET session = "{ip}" '
                        f'WHERE login = "{log}"')
                    users_cur.execute(
                        f'UPDATE users SET sestime = "{str(today)}" '
                        f'WHERE login = "{log}"')
                    users_cur.execute(
                        f'DELETE FROM requests WHERE user = "{log}";')
                    users_base.commit()
                    return jsonify({'login': True})
                else:
                    return jsonify(
                        {'error': 'Неверный код из телеграмма.'})
            except IndexError:
                return jsonify({'error': 'Неверный код из телеграмма.'})

        users_cur.execute(f'SELECT * FROM users WHERE login = "{log}"')
        user = users_cur.fetchone()

        if not user:
            return jsonify({'error': 'Проверьте правильность введенного '
                                     'логина или зарегистрируйтесь.'})

        if user[1] == pas:
            if user[6]:
                code = random.randint(10000, 99999)
                bot.send_message(user[6], f'Код для входа на сайт: {code}')
                users_cur.execute(f'INSERT INTO requests VALUES (?, ?, ?, ?)',
                                  ['login', log, code, ''])
                users_base.commit()
                return jsonify({'code': 'sent'})

            else:
                ip = request.remote_addr
                today = datetime.date.today()
                users_cur.execute(f'SELECT * FROM users WHERE '
                                  f'session = "{ip}"')
                ips = users_cur.fetchall()
                for i in ips:
                    users_cur.execute(
                        f'UPDATE users SET session = "" '
                        f'WHERE login = "{i[0]}"')
                users_cur.execute(
                    f'UPDATE users SET session = "{ip}" WHERE login = "{log}"')
                users_cur.execute(
                    f'UPDATE users SET sestime = "{str(today)}" '
                    f'WHERE login = "{log}"')

                new_session = [random.choice(asc) for _ in range(20)]
                new_session = ''.join(new_session)

                response = make_response(jsonify({'index': True}))
                response.set_cookie('token_session', new_session,
                                    60 * 60 * 24 * 30)

                users_cur.execute('INSERT INTO sessions VALUES (?, ?)',
                                  (log, new_session))

                users_base.commit()

                return response
        else:
            return jsonify({
                'error': 'Проверьте правильность введенного пароля или '
                         'зарегистрируйтесь.'})

    else:
        err = request.args.get('error')
        if err:
            err = int(err)
            return render_template('login.html', error=err)
        return render_template('login.html', error=0)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        ip = request.remote_addr
        q = request.form
        users_cur.execute(f'SELECT * FROM users WHERE login = "{q["login"]}"')
        user = users_cur.fetchall()

        if user:
            return render_template('register.html', error=1)
        elif len(q['password']) < 8:
            return render_template('register.html', error=2)
        elif q['password'] != q['password-2']:
            return render_template('register.html', error=3)
        today = datetime.date.today()

        pas = sha_password(q['password'])
        users_cur.execute('INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?);',
                          (q['login'], pas, ip, today, '', '', '', None))

        new_session = [random.choice(asc) for _ in range(20)]
        new_session = ''.join(new_session)

        response = make_response(redirect(url_for('index')))
        response.set_cookie('token_session', new_session,
                            60 * 60 * 24 * 30)

        users_cur.execute('INSERT INTO sessions VALUES (?, ?)',
                          (q['login'], new_session))

        users_base.commit()
        return response
    else:
        return render_template('register.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    cookie_session = request.cookies.get('token_session')

    if request.method == 'GET':
        if not cookie_session:
            return redirect(url_for('result_no_login',
                                    search=request.form['search'],
                                    search_type=request.form['search_type'],
                                    page=1))
        try:
            user = users_cur.execute('SELECT * FROM sessions '
                                     'WHERE session = ?',
                                     (cookie_session,)).fetchone()
            user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                                     (user[0],)).fetchone()
            _ = user[0]
        except TypeError:
            return redirect(url_for('result_no_login',
                                    search=request.form['search'],
                                    search_type=request.form['search_type'],
                                    page=1))

        text = request.args.get('search')
        search_type = request.args.get('search_type')
        if not text or text.isspace():
            return render_template('result.html', result=(),
                                   error='Запрос слишком короткий',
                                   page=0)

        if not text.isspace() and text:
            if search_type == '1':
                text = text.lower()
                text = text.split()
                text = [spell.correction(i) for i in text]
                mes = []
                for i in text:
                    a = morph.parse(i)[0].normal_form
                    a = f'text LIKE "%{a}%"'
                    mes.append(a)
                text = 'SELECT * FROM subtitles WHERE ' \
                       + ' AND '.join(mes)
                text_count = 'SELECT COUNT(text) FROM subtitles WHERE ' \
                             + ' AND '.join(mes)
            elif search_type == '0':
                saved, text = text, f'SELECT * FROM subtitles WHERE ' \
                       f'rawtext LIKE "%{text}%"'
                text_count = f'SELECT COUNT(text) FROM subtitles WHERE ' \
                             f'rawtext LIKE "%{saved}%"'
                print(text_count)
            else:
                half_raw_text = text.lower()
                half_raw_text = half_raw_text.replace(',', '')
                half_raw_text = half_raw_text.replace('.', '')
                half_raw_text = half_raw_text.replace('!', '')
                half_raw_text = half_raw_text.replace('-', '')
                half_raw_text = half_raw_text.replace('?', '')
                if not half_raw_text or half_raw_text.isspace():
                    return render_template('result.html', result=(),
                                           error='Запрос слишком короткий',
                                           page=0)
                text = f'SELECT * FROM subtitles WHERE ' \
                       f'half_raw_text LIKE "%{half_raw_text}%"'
                text_count = f'SELECT COUNT(text) FROM subtitles WHERE ' \
                             f'half_raw_text LIKE "%{half_raw_text}%"'

            page = int(request.args.get('page')) - 1

            text += f'LIMIT 20 OFFSET {page * 10}'

            cur.execute(text)
            results = cur.fetchall()
        else:
            results = ()
        res = []
        for rt in results:
            cur.execute(f'SELECT * FROM films WHERE id = {rt[4]}')
            film = cur.fetchone()

            a = [film[1], rt[0], rt[1], rt[2], film[2], None,
                 str(film[0])]

            res.append(a)

        like = users_cur.execute(f'SELECT * FROM liked WHERE userId = ?',
                                 [user[7]]).fetchone()

        if not like:
            like = []
        else:
            like = like[2].split('; ')

        text = request.args.get('search')
        if page == 0:
            n = cur.execute(text_count).fetchone()[0]
            if user[4]:
                new_history = user[4] + f'; {text}: ' \
                                        f'{n}: {search_type}'
            else:
                new_history = f'{text}: {n}: {search_type}'
            users_cur.execute(f'UPDATE users SET history = ? WHERE login = ?',
                              (new_history, user[0]))

        users_base.commit()

        return render_template('result.html', result=res, like=like,
                               page=page,
                               url1=f'/result?search={text}&search_type={search_type}&page={page + 2}',
                               url2=f'/result?search={text}&search_type={search_type}&page={page}')
    else:
        usid = request.form['id']

        user = users_cur.execute('SELECT * FROM sessions '
                                 'WHERE session = ?',
                                 (cookie_session,)).fetchone()
        user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                                 (user[0],)).fetchone()
        us = user[7]
        users_cur.execute(f'SELECT * FROM liked WHERE userId = "{us}"')
        res = users_cur.fetchone()
        if not res:
            users_cur.execute(f'INSERT INTO liked VALUES(?, ?, ?)',
                              (None, us, f'{usid}'))
            users_base.commit()
            return jsonify({'send': '1'})
        elif not res[2]:
            users_cur.execute(
                f'UPDATE liked SET filmIds = "{usid}" WHERE userId = "{us}"')
            users_base.commit()
            return jsonify({'send': '1'})

        if usid not in res[2].split('; '):
            users_cur.execute(
                f'UPDATE liked SET filmIds = "{res[2] + "; " + usid}"'
                f'WHERE userId = "{us}"')
            users_base.commit()
            return jsonify({'send': '1'})

        films = res[2].split('; ')
        films.remove(usid)
        films = '; '.join(films)
        users_cur.execute(
            f'UPDATE liked SET filmIds = "{films}" WHERE userId = "{us}"')
        users_base.commit()
        return jsonify({'notsend': '1'})


@app.route('/result_no_login', methods=['GET'])
def result_no_login():
    text = request.args.get('search')
    search_type = request.args.get('search_type')
    if not text and not text.isspace():
        return render_template('result-nologin.html',
                               result=(),
                               error='Запрос слишком короткий',
                               page=0)

    if not text.isspace() and text:
        if search_type == '1':
            text = text.lower()
            text = text.split()
            text = [spell.correction(i) for i in text]
            mes = []
            for i in text:
                a = morph.parse(i)[0].normal_form
                a = f'text LIKE "%{a}%"'
                mes.append(a)
            text = 'SELECT * FROM subtitles WHERE ' \
                   + ' AND '.join(mes)
        elif search_type == '0':
            text = f'SELECT * FROM subtitles WHERE ' \
                   f'rawtext LIKE "%{text}%"'
        else:
            half_raw_text = text.lower()
            half_raw_text = half_raw_text.replace(',', '')
            half_raw_text = half_raw_text.replace('.', '')
            half_raw_text = half_raw_text.replace('!', '')
            half_raw_text = half_raw_text.replace('-', '')
            half_raw_text = half_raw_text.replace('?', '')
            if not half_raw_text and not half_raw_text.isspace():
                return render_template('result-nologin.html',
                                       result=(),
                                       error='Запрос слишком короткий',
                                       page=0)
            text = f'SELECT * FROM subtitles WHERE ' \
                   f'half_raw_text LIKE "%{half_raw_text}%"'

        page = int(request.args.get('page')) - 1

        text += f'LIMIT 20 OFFSET {page * 10}'

        print(text)

        cur.execute(text)
        results = cur.fetchall()
    else:
        results = ()
    res = []
    for rt in results:
        cur.execute(f'SELECT * FROM films WHERE id = {rt[4]}')
        film = cur.fetchone()

        a = [film[1], rt[0], rt[1], rt[2], film[2], None,
             str(film[0])]

        res.append(a)

    text = request.args.get('search')

    return render_template('result-nologin.html', result=res,
                           page=page,
                           url1=f'/result_no_login?search={text}&search_type={search_type}&page={page + 2}',
                           url2=f'/result_no_login?search={text}&search_type={search_type}&page={page}')


@app.route('/profile', methods=['GET'])
def profile():
    cookie_session = request.cookies.get('token_session')

    if not cookie_session:
        return redirect(url_for('login', error=3))
    try:
        user = users_cur.execute('SELECT * FROM sessions '
                                 'WHERE session = ?',
                                 (cookie_session,)).fetchone()
        user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                                 (user[0],)).fetchone()
        _ = user[0]
    except TypeError:
        return redirect(url_for('login', error=3))

    if user[6]:
        return render_template('profile.html', tg=user[6])
    else:
        return render_template('profile.html', tg=0)


@app.route('/get_tg', methods=['POST'])
def get_tg():
    us = request.args.get('username')
    un = request.args.get('id')
    try:
        users_cur.execute('INSERT INTO tg VALUES(?, ?);', (un, us.lower()))
    except sqlite3.IntegrityError:
        return 'nthx'
    users_base.commit()
    return 'thx'


@app.route('/process', methods=['POST'])
def process():
    us = request.form['username']
    pas = sha_password(request.form['pass'])
    cookie_session = request.cookies.get('token_session')
    user = users_cur.execute('SELECT * FROM sessions '
                             'WHERE session = ?',
                             (cookie_session,)).fetchone()
    user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                             (user[0],)).fetchone()

    if user[1] == pas:
        users_cur.execute(f'SELECT * FROM tg WHERE username = "{us}"')
        telegram = users_cur.fetchone()
        if not telegram:
            return jsonify({'error': 'Вы не отправляли '
                                     'сообщения нашему боту.'})
        bot.send_message(telegram[0],
                         f'Проверочная ссылка, для подтверждения 2FA Доступа: '
                         f'https://filmfinder.ru/confirm?id={user[2] * 2}'
                         f'&tg={telegram[0]}')
        return jsonify({'send': True})
    else:
        return jsonify({'error': 'Неверно введен пароль'})


@app.route('/confirm')
def confirm():
    id_pass = request.args.get('id')
    tg = request.args.get('tg')
    users_cur.execute(f'UPDATE users SET tgid = "{tg}" '
                      f'WHERE session = "{id_pass[:len(id_pass) // 2]}"')
    users_base.commit()
    return render_template('confirm.html')


@app.route('/liked')
def liked():
    cookie_session = request.cookies.get('token_session')

    if not cookie_session:
        return redirect(url_for('login', error=3))
    try:
        user = users_cur.execute('SELECT * FROM sessions '
                                 'WHERE session = ?',
                                 (cookie_session,)).fetchone()
        user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                                 (user[0],)).fetchone()
        _ = user[0]
    except TypeError:
        return redirect(url_for('login', error=3))

    users_cur.execute(f'SELECT * FROM liked WHERE userId = "{user[7]}"')
    likes = users_cur.fetchone()
    if not likes:
        return render_template('liked.html', result=None, like=[])
    else:
        likes = likes[2].split('; ')
        cur.execute(f'SELECT * FROM films WHERE id in ({", ".join(likes)})')
        ld = cur.fetchall()
        for j, i in enumerate(ld):
            ld[j] = [str(i[0]), i[1], i[2]]
        return render_template('liked.html', result=ld, like=likes)


@app.route('/offtg', methods=['POST', 'GET'])
def offtg():
    cookie_session = request.cookies.get('token_session')
    user = users_cur.execute('SELECT * FROM sessions '
                             'WHERE session = ?',
                             (cookie_session,)).fetchone()
    users_cur.execute(f'UPDATE users SET tgid = "" WHERE login = ?', (user[0]))
    users_base.commit()
    return redirect(url_for('profile'))


@app.route('/passchange', methods=["POST"])
def pass_change():
    newp = sha_password(request.form['pass'])
    oldp = sha_password(request.form['oldpass'])

    cookie_session = request.cookies.get('token_session')

    if request.form['code']:
        code = request.form['code']
        users_cur.execute(f'SELECT * FROM requests WHERE '
                          f'code = "{code}" AND other = "{newp}"')
        if users_cur.fetchone():
            users_cur.execute(f'UPDATE users SET password = "{newp}" '
                              f'WHERE password = "{oldp}"')
            users_cur.execute(f'DELETE FROM requests WHERE other = "{newp}";')
            users_base.commit()
            return jsonify({'success': 'Пароль успешно сменен!'})
        else:
            return jsonify({'error': 'Введенный код неверен!'})

    else:
        newp2 = sha_password(request.form['pass_2'])
        another = request.form['pass_2']

        user = users_cur.execute('SELECT * FROM sessions '
                                 'WHERE session = ?',
                                 (cookie_session,)).fetchone()

        users_cur.execute(f'SELECT * FROM users WHERE login = "{user[0]}"')
        us = users_cur.fetchone()
        if us:
            if newp == newp2 and len(another) > 7:
                if us[6]:
                    num = random.randint(10000, 99999)
                    bot.send_message(us[6], f'Проверочный код '
                                            f'для смены пароля: {num}')
                    users_cur.execute(f'INSERT INTO requests '
                                      f'VALUES(?, ?, ?, ?)',
                                      ['changepass', us[0], num, newp])
                    users_base.commit()
                    return jsonify(
                        {'alert': 'В ваш телеграм отправлен проверочный код'})
                else:
                    users_cur.execute(f'UPDATE users SET password = '
                                      f'"{newp}" WHERE password = "{oldp}"')
                    users_base.commit()
                    return jsonify({'success': 'Пароль успешно сменен!'})
            else:
                return jsonify({'error': 'Пароли не совпадают или длина '
                                         'пароля недостаточна.'})
        else:
            return jsonify({'error': 'Неверный старый пароль'})


@app.route('/profile_act', methods=['POST'])
def setting():
    t = request.form['type']
    cookie_session = request.cookies.get('token_session')

    user = users_cur.execute('SELECT * FROM sessions '
                             'WHERE session = ?',
                             (cookie_session,)).fetchone()
    user = users_cur.execute('SELECT * FROM users WHERE login = ?',
                             (user[0],)).fetchone()

    if t == 'clearhistory':
        users_cur.execute('UPDATE users SET history = "" WHERE login = ?',
                          (user[0],))
        users_base.commit()

        return jsonify({'delete': 'История поиска очищена'})

    if t == 'clearliked':
        users_cur.execute(f'UPDATE liked SET FilmIds = "" '
                          f'WHERE userId = "{user[7]}"')
        users_base.commit()

        return jsonify({'delete': 'Ваши понравившиеся очищены'})

    else:
        users_cur.execute(f'UPDATE users SET session = "" WHERE login = ?',
                          (user[0],))
        users_base.commit()
        response = make_response(jsonify({'delete': 'Выход успешен'}))
        response.set_cookie('token_session', '', 0)
        return response


@app.route('/developers')
def developers():
    return render_template('api.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_500_error(e):
    return render_template('500.html'), 500


@app.errorhandler(502)
def page_502_error(e):
    return render_template('500.html'), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
