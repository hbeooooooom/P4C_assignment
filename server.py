import pymysql
import os
from flask import Flask, render_template, url_for, request, redirect, flash, session, send_from_directory
from werkzeug.utils import secure_filename


def create_database():
    db_connection = pymysql.connect(host="localhost", user="root", passwd="1234", charset="utf8")
    cursor = db_connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS free_board_image5")
    cursor.execute("USE free_board_image5") 
    cursor.execute("""CREATE TABLE IF NOT EXISTS board_image (
                      num INT NOT NULL,
                      title VARCHAR(50) NOT NULL,
                      writer VARCHAR(50) NOT NULL,
                      context VARCHAR(200) NOT NULL,
                      file_name VARCHAR(200),
                      file_path VARCHAR(200),
                      password VARCHAR(100),
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    db_connection.close()

    db_connection = pymysql.connect(host="localhost", user="root", passwd="1234", charset="utf8")
    cursor = db_connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS regist_board")
    cursor.execute("USE regist_board") 
    cursor.execute("""CREATE TABLE IF NOT EXISTS tb_user (
                      useridx int primary key auto_increment,
                      userid varchar(100) unique NOT NULL,
                      userpw varchar(100) NOT NULL,
                      username varchar(100) NOT NULL,
                      useremail varchar(100) NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    db_connection.close()
create_database()



check_num = 1
app = Flask(__name__) 
app.secret_key = '123'

@app.route('/', methods=['GET', 'POST'])
def index():
    db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
    cursor = db.cursor()
    global check_num
    if request.method == 'POST':
        search_option = request.form['option']
        search_name = request.form['search']
        if search_option == "전체 기준 검색":
            query = "SELECT * FROM board WHERE "
            columns = ["title", "context", "writer"]  
            conditions = []
            for column in columns:
                conditions.append(f"{column} LIKE %s")
            query += " OR ".join(conditions)
            cursor.execute(query, tuple(['%' + search_name + '%'] * len(columns)))
            data_list = cursor.fetchall()
        elif search_option == "제목 기준 검색":
            cursor.execute("SELECT * FROM board_image WHERE title LIKE %s", ('%' + search_name + '%'))
            data_list = cursor.fetchall()
        elif search_option == "내용 기준 검색":
            cursor.execute("SELECT * FROM board_image WHERE context LIKE %s", ('%' + search_name + '%'))
            data_list = cursor.fetchall()
    else:
        sql = "SELECT * FROM board_image"
        cursor.execute(sql)
        data_list = cursor.fetchall()
        for i in data_list:
            check_num = i[0]
            check_num = check_num + 1
    db.close()
    return render_template('index.html', data_list=data_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form['userid']
        pw = request.form['userpw']
        name = request.form['username']
        email = request.form['useremail']

        if id and pw and name and email:
            db = pymysql.connect(host="localhost", user="root", passwd="1234", db='regist_board', charset="utf8")
            cursor = db.cursor()
            cursor.execute("INSERT INTO tb_user (userid, userpw, username, useremail) VALUES (%s,%s,%s,%s)", (id, pw, name, email))
            db.commit()
            db.close()
            return redirect(url_for('index'))
    else: 
        return render_template("register.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        id = request.form['userid'] 
        pw = request.form['userpw']

        if id and pw:
            db = pymysql.connect(host="localhost", user="root", passwd="1234", db='regist_board', charset="utf8")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tb_user WHERE userid = %s AND userpw = %s", (id, pw))
            user_account = cursor.fetchone()

            if user_account:
                session['id'] = id
                db.close()
                return redirect(url_for('index'))
            else:
                flash('Login failed. Please check your credentials.', 'error')
                db.close()
                return redirect(url_for('login'))
    else:
        return render_template("login.html")

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))
    
@app.route('/findpw', methods=['GET','POST'])
def findpw():
    if request.method == 'GET':
        return render_template('findpw.html')
    else:
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='regist_board', charset="utf8")
        cursor = db.cursor()
        email = request.form['email']
        id = request.form['id']
        cursor.execute("SELECT userpw FROM tb_user WHERE useremail = %s AND userid = %s",(email,id))
        data = cursor.fetchone()
        db.close()
        return redirect(url_for('resultpw', data=data[0]))

@app.route('/resultpw/<data>')
def resultpw(data):
    return render_template('resultpw.html', data=data)

@app.route('/findid', methods=['GET','POST'])
def findid():
    if request.method == 'GET':
        return render_template('findid.html')
    else:
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='regist_board', charset="utf8")
        cursor = db.cursor()
        email = request.form['email']
        cursor.execute("SELECT userid FROM tb_user WHERE useremail = %s",(email))
        data = cursor.fetchone()
        db.close()
        return redirect(url_for('resultid', data=data[0]))

@app.route('/resultid/<data>')
def resultid(data):
    return render_template('resultid.html', data=data)

@app.route('/secret/<num>', methods=['GET', 'POST'])
def secret(num):
    if request.method == 'POST':
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        password = request.form['password'] 
        cursor.execute("SELECT * FROM board_image WHERE num = %s AND password = %s", (num, password))
        true_check = cursor.fetchone()
        db.close()
        if true_check:
            return redirect(url_for('view', num=num))
        if not true_check:
            return redirect(url_for('index'))
    else:
        return render_template('secret.html', num=num)


@app.route('/view/<num>', methods=['GET'])
def view(num):
    if request.method == 'GET':
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        cursor.execute('SELECT * FROM board_image WHERE num = %s', (num))
        data = cursor.fetchall()
        db.close()
        return render_template('view.html', data = data[0])

@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    directory = 'static/uploads'
    return send_from_directory(directory, filename)

@app.route('/write', methods=['GET', 'POST'])
def write():
    global check_num
    if request.method == 'POST':
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        title = request.form['title']
        writer = request.form['writer']
        context = request.form['context']
        img = request.files['file']
        password = request.form['password']
        if password and img:
            img.save('static/uploads/'+secure_filename(img.filename))
            cursor.execute("INSERT INTO board_image (num, title, writer, context, file_name, file_path, password) VALUES (%s,%s,%s,%s,%s,%s,%s)", (check_num, title, writer, context,img.filename,'uploads/'+secure_filename(img.filename),password))
        elif password:
            cursor.execute("INSERT INTO board_image (num, title, writer, context, password) VALUES (%s,%s,%s,%s,%s)", (check_num, title, writer, context,password))
        elif img:
            img.save('static/uploads/'+secure_filename(img.filename))
            cursor.execute("INSERT INTO board_image (num, title, writer, context, file_name, file_path) VALUES (%s,%s,%s,%s,%s,%s)", (check_num, title, writer, context,img.filename,'uploads/'+secure_filename(img.filename)))
        else:
            cursor.execute("INSERT INTO board_image (num, title, writer, context) VALUES (%s,%s,%s,%s)", (check_num, title, writer, context))
        
        db.commit()
        check_num += 1
        db.close()
        return redirect(url_for('index'))
    else:
        return render_template('write.html')

        
@app.route('/edit/<num>', methods=['GET','POST'])
def edit(num):
    if request.method == 'GET':
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        cursor.execute('SELECT * FROM board_image WHERE num = %s', (num))
        data = cursor.fetchall()
        db.close()
        return render_template('edit.html', data = data[0])
    else:
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        title = request.form['title']
        writer = request.form['writer']
        context = request.form['context']
        cursor.execute("UPDATE board_image SET title = %s, writer = %s, context = %s WHERE num = %s",(title,writer,context,num))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    

@app.route('/delete/<num>', methods=['GET'])
def delete(num):
    if request.method=='GET':
        db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board_image5', charset="utf8")
        cursor = db.cursor()
        cursor.execute('DELETE FROM board_image WHERE num = %s', (num))
        db.commit()
        db.close()
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)