# app.py

import os
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
from datetime import datetime
from flask import request, redirect, abort, session, jsonify
import pymysql
import random 

app = Flask(__name__, 
            static_folder="static",
            template_folder="views"
            )
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = b'project'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60

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
    if 'user' in session:
        session.pop('user', None)
        return redirect('/index')
    
    else:

        title = "Login Page"
        message = ""
        if request.method == 'POST':
            cursor = db.cursor()
            cursor.execute(f"""
                select id, nickname, profile password from user
                where nickname = '{request.form['id']}'"""
            )
            user = cursor.fetchone()

            if user is None:
                message = "<p>회원이 아닙니다.</p>"
            else:
                cursor.execute(f"""
                    select id, nickname, password from user
                    where nickname = '{request.form['id']}' and
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

@app.route("/profile", methods=['get','post'])
def profile():
    cursor = db.cursor()
    cursor.execute(f"""
    select id, nickname, profile, name ,password, birthdate from user
    where nickname = '{session['user']['nickname']}' """)
    user = cursor.fetchone()
    
    id = session['user']['nickname']
    name = user['name']
    birthdate = user['birthdate']
    profile = user['profile']
    title = ""
    message = ""
    cursor = db.cursor()
    if request.method == 'GET':
        return render_template("profile.html",
                                title='',
                                id=id,
                                name=name,
                                profile=profile,
                                birthdate=birthdate,
                                message=message)
    elif request.method == 'POST':
        if request.form['pw'] != request.form['repw']:
            message=f"패스워드가 일치하지 않습니다."
            return render_template("profile.html",
                                    title='',
                                    id=id,
                                    name=name,
                                    profile=profile,
                                    birthdate=birthdate,
                                    message=message)
        if request.form['pw'] != "":
            sql = f"""
                update user set 
                password = '{request.form['pw']}'
                where nickname = '{id}'
            """    
            cursor.execute(sql)
            db.commit()
        if request.form['profile'] != "":
            sql = f"""
                update user set 
                profile = '{request.form['profile']}'
                where nickname = '{id}'
            """    
            cursor.execute(sql)
            db.commit()

        return redirect('/index')

def crawler_picture(word):
    def download_img_from_tag(tag, filename):
        response = requests.get(tag['data-source'])
        with open(filename, 'wb') as f:
            f.write(response.content)

    url = f"https://search.naver.com/search.naver?where=image&sm=tab_jum&query={word}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tags = soup.select('img._img')

    filenames = []
    for i, tag in enumerate(tags):
        filename = f'static/{word}{i}.jpg'
        download_img_from_tag(tag, filename)
        filenames.append(filename)
    return render_template('crawler.html',
                            files = filenames)

@app.route("/Photos", methods = ['GET', 'POST'])
def Photos():
    find = ""
    if request.method == 'GET':
        return render_template('content.html',
                                id = session['user']['nickname'],
                                title = "Photos",
                                option = "사진",
                                content = "",
                                menu = get_menu()
                                )

    elif request.method == 'POST':
        find =request.form['find']
        content = crawler_picture(find)
        return render_template('content.html',
                                id = session['user']['nickname'],
                                title = "Photos",
                                option = "사진",
                                content = content,
                                menu = get_menu())

@app.route("/News", methods = ['get', 'post'])
def News():
    if request.method == 'GET':
        return render_template('content.html',
                                id = session['user']['nickname'],
                                title = "News",
                                option = "뉴스",
                                content = "",
                                menu = get_menu()
                                )
    elif request.method == 'POST':
        find = request.form["find"]
        content = crawler_news(find)
        return render_template('content.html',
                                id = session['user']['nickname'],
                                title = "News",
                                option = "뉴스",
                                content = content,
                                menu = get_menu()
                                )
def crawler_news(word):
    url = f"https://search.naver.com/search.naver?query={word}&where=news&ie=utf8&sm=nws_hty"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    content = ""
    raw = soup.select('.type01')[0].select('._sp_each_title')
    for i in raw:
        text = i.get_text()
        href = i['href'] 
        content += f'<a href="{href}" target ="_blank"> {text} </a><br>'
    return content
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # return soup



def gameCalculate(answer, user_number):
    cursor = db.cursor()   
    answer_number = str(answer['game_number'])
    tryCount = answer['try_count']
    strike = 0; ball = 0; out = 0;
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
        sql = f"""
            update baseball set
                completed = True,
                try_count = '{(tryCount+1)}'
            where id = '{answer['id']}'
        """  
        cursor.execute(sql)
        db.commit()
        return f"{tryCount+1} 번만에 맞히셨습니다."
    else:
        sql = f"""
            update baseball set
                try_count = '{(tryCount+1)}'
            where id = '{answer['id']}'
        """  
        cursor.execute(sql)
        db.commit()
        return f"{strike}strike {ball}ball {out}out 입니다. \n {tryCount+1} 번 틀리셨습니다."

@app.route("/initGame", methods = ['get','post'])
def gamestart():
    cursor = db.cursor()
    while True:
        gameNumber = str(random.randint(100, 999))
        if len(gameNumber) == len(set(gameNumber)):
            break
    sql = f"""
        insert into baseball (nickname, created,game_number)
        values ('{session['user']['nickname']}', '{datetime.now()}','{int(gameNumber)}')
    """

    cursor.execute(sql)
    db.commit()
    return redirect('/Baseball')

def getAnswer():
    cursor = db.cursor()
    sql = f"""
        select id, game_number,try_count from baseball 
        where nickname = '{session['user']['nickname']}' 
        order by created desc limit 1
    """   
    cursor.execute(sql)
    return cursor.fetchone()

def getScore():
    score = ""
    cursor = db.cursor()
    sql = f"""
        select a.nickname, b.name, a.try_count 
        from baseball a, user b 
        where a.nickname = b.nickname and a.completed = 1
        order by a.try_count limit 5 ;
    """
    cursor.execute(sql)
    rawScore = cursor.fetchall()
    score = f"""
            <table border='1'> 
            <th>ID</th>
            <th>이름</th>
            <th>시도횟수</th>
     """
    for row in rawScore:
        print(row)
        score += f"<tr><td>{row['nickname']}</td> <td>{row['name']} </td> <td>{row['try_count']}</td></tr>"

    score += f"</table>"
    return score
@app.route("/Baseball", methods = ['get', 'post'])
def baseball():
    message = "Baseball Game"
    title ="Baseball Game"
    if 'user' in session:
        if request.method == 'GET':
            score = getScore()
            return render_template('baseball.html',
                                    id=session['user']['nickname'],
                                    title=title,
                                    message=message,
                                    score=score,
                                    menu=get_menu()
                                    )
        if request.method == 'POST':
            answer = getAnswer()
            score = getScore()
            message = gameCalculate(answer,request.form['number'])
            return render_template('baseball.html',
                        id=session['user']['nickname'],
                        title=title,
                        message=message,
                        score=score,
                        menu=get_menu()
                        )
    else:
        return redirect('/')


app.run(port="8002")