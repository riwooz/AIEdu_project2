# app.py

import os
from flask import Flask, render_template
from datetime import datetime
from flask import request, redirect, abort, session, jsonify
import pymysql

app = Flask(__name__, 
            static_folder="static",
            template_folder="views"
            )
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = b'project'

db = pymysql.connect(
    user='root',
    passwd='',
    host='localhost',
    db='project2',
    cursorclass=pymysql.cursors.DictCursor
)

def get_profile():
    cursor = db.cursor()
    cursor.execute("select * from user")
    profile = [f"<p><input type='text' name = {column[' ']} placeholder={column[' ']}></p>"
                for column in cursor.fetchall()]
    return '\n'.join(profile)

@app.route("/", methods = ['get', 'post'])
def login():
    title = "Login Page"
    message = ""
    if request.method == 'POST':
        cursor = db.cursor()
        cursor.execute(f"""
            select id, name, profile password from user
            where name = '{request.form['id']}'"""
        )
        user = cursor.fetchone()

        if user is None:
            message = "<p>회원이 아닙니다.</p>"
        else:
            cursor.execute(f"""
                select id, name, profile, password from user
                where name = '{request.form['id']}' and
                password = SHA2('{request.form['pw']}', 256)""")
            user = cursor.fetchone()

            if user is None:
                message = "<p>패스워드를 확인해 주세요.</p>"
            else:
                session['user'] = user
                return redirect("/index")
    return render_template('login.html',
                            titie=title,
                            message=message)

@app.route('/logout', methods = ['get'])
def logout():
    if 'user' in session:
        session.pop('user', None)
        return redirect('/')
        
    else:
        return redirect('/')

@app.route("/createmember", methods = ['get', 'post'])
def createMember():
    if request.method == 'GET':
        return render_template('createmember.html',
                                message='')
    elif request.method == 'POST':
        if request.form['pw'] != request.form['repw']:
            message=f"패스워드가 일치하지 않습니다."
            return render_template("createmember.html",
                                    title='',
                                    message=message)
        cursor = db.cursor()
        sql = f"""
            insert into user (nickname, password, name, profile, birthdate)
            values ('{request.form['nickname']}', SHA2('{request.form['pw']}',256), 
                    '{request.form['name']}', '{request.form['profile']}', 
                    '{request.form['birthdate']}000000')
        """
        cursor.execute(sql)
        db.commit()

        return redirect('/')


def get_menu():
    cursor = db.cursor()
    cursor.execute("select title, description from topic")
    menu = [f"<li><a href='/{row['title']}'>{row['description']}</a></li>"
            for row in cursor.fetchall()]
    return '\n'.join(menu)

@app.route("/index")
def index():
    if 'user' in session:
        title = "Main Page"
        content = "<img src='https://source.unsplash.com/featured/?south america,?mountain' height=100% width=100%>"
        return render_template('template.html',
                                # id=['user']['nickname']
                                id=session['user']['nickname'],
                                title=title,
                                content=content,
                                menu=get_menu()
                                )
    else:
        return redirect('/')

    # return render_templates('te.html',
    #                         columns=[{'name': 'id', 'placeholder': 'userid'}])


def createAnswerNumber(filename):
    while True:
        value = str(random.randint(100, 999))
        if len(value) == len(set(value)):
            break
    with open(f'game/{filename}', 'w') as f:
        f.write(value)

def gameCalculate(user_number):
    with open(f'game/answernumber', 'r') as f:
        answer_number = f.read()
    strike = 0
    ball = 0
    out = 0


    count = int(readFile('game/count_try'))
    writeFile('game/count_try',count+1)
    
    if len(user_number) != len(set(user_number)):
        return "중복 없이 다시 입력하세요."
    elif len(answer_number) != len(set(user_number)):
        return "숫자 자리수가 맞지 않습니다. 자리수에 맞게 다시 입력하세요."
    else:
        for i in range(len(user_number)):
            if user_number[i] == answer_number[i]:
                strike += 1
            elif user_number[i] in answer_number:
                ball += 1
            else: 
                out += 1
    if strike == len(answer_number):
        writeFile('game/count_try',0)        
        return "{0} 번만에 맞히셨습니다.".format(count)
    else:
        return "{0}strike {1}ball {2}out 입니다. \n {3} 번 틀리셨습니다.".format(strike, ball, out, count)
       

@app.route("/baseball", methods = ['get', 'post'])
def baseball():
    if 'user' in session:
        if request.method == 'GET':
        title ="Baseball Game"
        content =f"""
                        <p> <a href="/gamestart"><button>START!!!</button></a></p>
                        <form action="/playgame", method="post">
                            <p>숫자를 입력하세요 <input type="text", name="number">
                            <button type="submit">제출</button>
                            </p>

                        </form>
        """
        return render_template('template.html',
                                id=session['user']['nickname'],
                                title=title,
                                content=content,
                                menu=get_menu()
                                )
    else:
        return redirect('/')


app.run(port="8002")