from flask import Flask, render_template, request
from flask_api import status
import sqlite3
import json
app = Flask(__name__)

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

#0
@app.route('/api/v1/users', methods = ["GET"])
def displayUsers():
    conn = sqlite3.connect('database.db')
    users = conn.execute('SELECT USERNAME FROM USERS')
    usernames = [row[0] for row in users]
    return json.dumps(usernames), status.HTTP_200_OK

#1
@app.route('/user.html')
def userpage():
    return render_template('addUser.html')

@app.route('/api/v1/users', methods = ['POST'])
def addUser():
    conn = sqlite3.connect('database.db')
    users = conn.execute('SELECT USERNAME FROM USERS')
    usernames = [row[0] for row in users]
    if request.json['username'] in usernames:
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    if not is_sha1(request.json['password']):
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    conn.execute('INSERT INTO USERS VALUES ("' + request.json['username'] + '"' + ',' + '"' + request.json['password'] + '"' + ')')
    conn.commit()
    conn.close()
    return "{}", status.HTTP_201_CREATED

#2
@app.route('/remove.html')
def remove():
    return render_template('removeUser.html')

@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def removeUser(username):
    conn = sqlite3.connect('database.db')
    users = conn.execute('SELECT USERNAME FROM USERS')
    usernames = [row[0] for row in users]
    if username in usernames:
        conn.execute('DELETE FROM USERS WHERE USERNAME = "' + username + '"')
        conn.execute('DELETE FROM ACTS WHERE USERNAME = "' + username + '"')
        conn.commit()
        conn.close()
        return "{}", status.HTTP_200_OK
    conn.close()
    return "{}", status.HTTP_400_BAD_REQUEST

if __name__ == '__main__':
   app.run(host = '0.0.0.0', port = 80, debug = True)
