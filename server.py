import pymysql
from flask import Flask, render_template, url_for, request, redirect

def create_database():
    db_connection = pymysql.connect(host="localhost", user="root", passwd="1234", charset="utf8")
    cursor = db_connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS free_board")
    cursor.execute("USE free_board")
    cursor.execute("""CREATE TABLE IF NOT EXISTS board (
                      num INT NOT NULL,
                      title VARCHAR(50) NOT NULL,
                      writer VARCHAR(50) NOT NULL,
                      context VARCHAR(200) NOT NULL)""")
    db_connection.close()

create_database()


db = pymysql.connect(host="localhost", user="root", passwd="1234", db='free_board', charset="utf8")
cursor = db.cursor()
check_num = 1
app = Flask(__name__) 

@app.route('/', methods=['GET', 'POST'])
def index():
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
            cursor.execute("SELECT * FROM board WHERE title LIKE %s", ('%' + search_name + '%'))
            data_list = cursor.fetchall()
        elif search_option == "내용 기준 검색":
            cursor.execute("SELECT * FROM board WHERE context LIKE %s", ('%' + search_name + '%'))
            data_list = cursor.fetchall()
    else:
        sql = "SELECT * FROM board"
        cursor.execute(sql)
        data_list = cursor.fetchall()
        for i in data_list:
            check_num = i[0]
            check_num = check_num + 1
    return render_template('index.html', data_list=data_list)

@app.route('/write', methods=['GET','POST'])
def write():
    global check_num
    if request.method == 'POST':
        title = request.form['title']
        writer = request.form['writer']
        context = request.form['context']
        cursor.execute("INSERT INTO board (num, title, writer, context) VALUES (%s,%s,%s,%s)", (check_num, title, writer, context))
        db.commit()
        check_num = check_num + 1
        return redirect(url_for('index'))
    else:
        return render_template('write.html')
        
@app.route('/edit/<num>', methods=['GET','POST'])
def edit(num):
    if request.method == 'GET':
        cursor.execute('SELECT * FROM board WHERE num = %s', (num))
        data = cursor.fetchall()
        return render_template('edit.html', data = data[0])
    else:
        title = request.form['title']
        writer = request.form['writer']
        context = request.form['context']
        cursor.execute("UPDATE board SET title = %s, writer = %s, context = %s WHERE num = %s",(title,writer,context,num))
        db.commit()
        return redirect(url_for('index'))
    

@app.route('/delete/<num>', methods=['GET'])
def delete(num):
    if request.method=='GET':
        cursor.execute('DELETE FROM board WHERE num = %s', (num))
        db.commit()
    
    return redirect(url_for('index'))
    



if __name__ == "__main__":
    app.run(debug=True)