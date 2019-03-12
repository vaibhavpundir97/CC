from flask import Flask, render_template, request
from flask_api import status
import sqlite3
import json
import time
import base64
import binascii
from collections import Counter
import re
app = Flask(__name__)

def changeTime(timestamp, bool = False):
    if bool:
        return timestamp[6:10] + '-' + timestamp[3:5] + '-' + timestamp[0:2] + ' ' + timestamp[17:] + ':' + timestamp[14:16] + ':' + timestamp[11:13]
    return timestamp[8:10] + '-' + timestamp[5:7] + '-' + timestamp[0:4] + ':' + timestamp[17:] + '-' + timestamp[14:16] + '-' + timestamp[11:13]

#3
@app.route('/api/v1/categories', methods = ["GET"])
def listCategories():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT CATEGORYNAME FROM ACTS')
    categories = [row[0] for row in cursor]
    category_freq = dict(Counter(categories))
    return json.dumps(category_freq), status.HTTP_200_OK
    conn.close()

#4
@app.route('/addcat.html')
def addcat():
    return render_template('addCat.html')

@app.route('/api/v1/categories', methods = ["POST"])
def insertCategory():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT * FROM CATEGORY')
    categories = [row[0] for row in cursor]
    if len(request.json) == 0 or request.json[0] in categories:
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    conn.execute('INSERT INTO CATEGORY VALUES ("' + request.json[0] + '")')
    conn.commit()
    conn.close()
    return "{}", status.HTTP_201_CREATED

#5
@app.route('/cremove.html')
def cremove():
    return render_template('removeCat.html')

@app.route('/api/v1/categories/<categoryname>', methods = ["DELETE"])
def removeCategory(categoryname):
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT * FROM CATEGORY')
    if categoryname not in [row[0] for row in cursor]:
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    conn.execute('DELETE FROM ACTS WHERE CATEGORYNAME = "' + categoryname + '"')
    conn.execute('DELETE FROM CATEGORY WHERE CATEGORYNAME = "' + categoryname + '"')
    conn.commit()
    conn.close()
    return "{}", status.HTTP_200_OK

#6
@app.route('/listact.html')
def listact():
    return render_template('listActs.html')

@app.route('/api/v1/categories/<categoryname>/acts', methods = ["GET"])
def listActs(categoryname):
    if len(request.args) == 2:
        return catRange(categoryname, int(request.args.get('start')), int(request.args.get('end')))
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT CATEGORYNAME FROM ACTS')
    if categoryname not in [row[0] for row in cursor]:
        conn.close()
        return "[]", status.HTTP_400_BAD_REQUEST
    cursor = conn.execute('SELECT * FROM ACTS WHERE CATEGORYNAME = "' + categoryname + '" ORDER BY TIMESTAMP DESC')
    rows = cursor.fetchall()
    if len(rows) >= 100:
        conn.close()
        return "[]", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    out = []
    for row in rows:
        out.append({'actId': row[0], 'username': row[1], 'timestamp': changeTime(row[2]), 'caption': row[3], 'upvotes': row[4], 'imgB64': row[6]})
    conn.close()
    return json.dumps(out), status.HTTP_200_OK

#7
@app.route('/size.html')
def size():
    return render_template("catSize.html")

@app.route('/api/v1/categories/<categoryname>/acts/size', methods = ["GET"])
def categorySize(categoryname):
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT COUNT(*) FROM ACTS WHERE CATEGORYNAME = "' + categoryname + '"')
    for row in cursor:
        return json.dumps(row[0]), status.HTTP_200_OK

#8
@app.route('/crange.html')
def crange():
    return render_template("catRange.html")

def catRange(categoryname, startRange, endRange):
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT CATEGORYNAME FROM ACTS')
    if categoryname not in [row[0] for row in cursor]:
        conn.close()
        return "[]", status.HTTP_400_BAD_REQUEST
    if endRange - startRange + 1 > 100:
        return "[]", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    cursor = conn.execute('SELECT * FROM ACTS WHERE CATEGORYNAME = "' + categoryname + '" ORDER BY TIMESTAMP DESC')
    rows = cursor.fetchall()
    if startRange < 1 or  endRange > len(rows):
        return "[]", status.HTTP_400_BAD_REQUEST
    out = []
    for row in rows:
        out.append({'actId': row[0], 'username': row[1], 'timestamp': changeTime(row[2]), 'caption': row[3], 'upvotes': row[4], 'imgB64': row[6]})
    conn.close()
    return json.dumps(out[startRange-1:endRange]), status.HTTP_200_OK

#9
@app.route('/api/v1/acts/upvote', methods = ["POST"])
def upvote():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT ACTID FROM ACTS')
    if request.json[0] not in [row[0] for row in cursor]:
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    conn.execute('UPDATE ACTS SET UPVOTES = UPVOTES + 1 WHERE ACTID = ' + str(request.json[0]))
    conn.commit()
    conn.close()
    return "{}", status.HTTP_200_OK

#10
@app.route('/api/v1/acts/<actid>', methods = ["DELETE"])
def removeAct(actid):
    if actid != 'upvote':
        conn = sqlite3.connect('database.db')
        cursor = conn.execute('SELECT ACTID FROM ACTS')
        if int(actid) not in [row[0] for row in cursor]:
            conn.close()
            return "{}", status.HTTP_400_BAD_REQUEST
        conn.execute('DELETE FROM ACTS WHERE ACTID = ' + actid)
        conn.commit()
        conn.close()
        return "{}", status.HTTP_200_OK

#11
@app.route('/upload.html')
def upload():
    return render_template('upload.html')

@app.route('/api/v1/acts', methods = ["POST"])
def uploadAct():
    conn = sqlite3.connect('database.db')
    cursor = conn.execute('SELECT USERNAME FROM USERS')
    if request.json['username'] not in [row[0] for row in cursor]:
        conn.close()
        print("user")
        return "{}", status.HTTP_400_BAD_REQUEST
    cursor = conn.execute('SELECT ACTID FROM ACTS')
    if request.json['actId'] in [row[0] for row in cursor]:
        conn.close()
        print("id")
        return "{}", status.HTTP_400_BAD_REQUEST
    cursor = conn.execute('SELECT CATEGORYNAME FROM CATEGORY')
    if request.json['categoryName'] not in [row[0] for row in cursor]:
        conn.close()
        print("category")
        return "{}", status.HTTP_400_BAD_REQUEST
    pattern = '(\d{2})-(\d{2})-(\d{4}):(\d{2})-(\d{2})-(\d{2})'
    if not re.match(pattern, request.json['timestamp']):
        conn.close()
        print("time")
        return "{}", status.HTTP_400_BAD_REQUEST
    if 'upvotes' in request.json.keys():
        conn.close()
        return "{}", status.HTTP_400_BAD_REQUEST
    conn.execute('INSERT INTO ACTS VALUES (' + str(request.json['actId']) + ', "' + request.json['username'] + '", "' + changeTime(request.json['timestamp'], True) + '", "' + request.json['caption'] + '", 0, "' + request.json['categoryName'] + '", "' + request.json['imgB64'] + '")')
    conn.commit()
    return "{}", status.HTTP_201_CREATED

if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug = True)
