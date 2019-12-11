
#-*- coding:utf-8 -*-



# mysql -uroot -p
# passward: mysql


from flask import Flask, render_template, request, jsonify, make_response

from flaskext.mysql import MySQL
import pymysql
import json
import requests
import sys
from importlib import reload

reload(sys)



app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mysql'
app.config['MYSQL_DATABASE_DB'] = 'ccc'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8'
mysql.init_app(app)

# READ DATABASE

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/post_vector')
def post_vector():
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # cursor.execute("SELECT idx,emotion,V1,V2 from posts")
    # data = cursor.fetchall()
    # data = list(data)
    # result = list(map(list,data))[1:]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id,emotion,V1,V2 from posts")
    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    rv = cursor.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    # result = [(v1,v2)]
    # result = result + data

    return render_template('post_vector.html', result=json.dumps(json_data[1:]))

@app.route('/info')
def get_info():
    id = request.args.get("id")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ccc.posts WHERE id =" + id)
  
    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    rv = cursor.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    data = json_data[0]
  
    return make_response(json.dumps(data, ensure_ascii=False).encode('utf8'))


@app.route('/user')
def get_user():
    user = request.args.get("user")
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ccc.posts WHERE user ='" + user+"'")
  
    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    rv = cursor.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

  
    return make_response(json.dumps(json_data, ensure_ascii=False).encode('utf8'))


@app.route('/user_vector')
def user_vector():
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # cursor.execute("SELECT idx,emotion,V1,V2 from posts")
    # data = cursor.fetchall()
    # data = list(data)
    # result = list(map(list,data))[1:]
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user,emotion,V1,V2 from users")
    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    rv = cursor.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    # result = [(v1,v2)]
    # result = result + data

    return render_template('user_vector.html', result=json.dumps(json_data[1:]))



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")