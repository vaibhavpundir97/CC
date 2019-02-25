from flask import Flask, render_template, request
from flask_api import status
import json
import time
import base64
import binascii
app = Flask(__name__)

@app.route('/')
def homepage():
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    result = {}
    for key, value in data.items():
        if len(value) != 0:
            result[key] = value
    return render_template('index.html', result = result)

#1
@app.route('/user.html')
def userpage():
    return render_template('addUser.html')

@app.route('/api/v1/users', methods = ['POST'])
def addUser():
    if request.method == "POST":
        users = open('users.json')
        data = json.load(users)
        users.close()
        for i in range(len(data['credentials'])):
            if data['credentials'][i]['username'] == request.json["username"]:
                return "{}", status.HTTP_400_BAD_REQUEST
        users = open('users.json', 'w')
        data['credentials'].append(request.json)
        json.dump(data, users)
        users.close()
        return "{}", status.HTTP_201_CREATED

#2
@app.route('/remove.html')
def remove():
    return render_template('removeUser.html')

@app.route('/api/v1/users/<username>', methods = ["DELETE"])
def removeUser(username):
    if request.method == "DELETE":
        users = open('users.json')
        data = json.load(users)
        users.close()
        for i in range(len(data['credentials'])):
            if data['credentials'][i]['username'] == username:
                data['credentials'].pop(i)
                users = open('users.json', 'w')
                json.dump(data, users)
                users.close()
                acts = open('acts.json')
                data = json.load(acts)
                acts.close();
                actid = open('actid.json')
                dataid = json.load(actid)
                actid.close()
                for key, value in data.items():
                    for i in value:
                        if i['username'] == username:
                            dataid['ID'].remove(i['actId'])
                            data[key].remove(i)
                acts = open('acts.json', 'w')
                json.dump(data, acts)
                acts.close();
                actid = open('actid.json', 'w')
                json.dump(dataid, actid)
                actid.close()
                return "{}", status.HTTP_200_OK
        return "{}", status.HTTP_400_BAD_REQUEST

#3,4
@app.route('/addcat.html')
def addcat():
    return render_template('addCat.html')

@app.route('/api/v1/categories', methods = ["GET", "POST"])
def listCategories():
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    if request.method == "GET":
        result = {}
        for key, value in data.items():
            result[key] = len(value)
        if result == {}:
            return json.dumps(result), status.HTTP_204_NO_CONTENT
        return json.dumps(result), status.HTTP_200_OK
    else:
        for key, value in data.items():
            if request.json == {}:
                return "{}", status.HTTP_405_METHOD_NOT_ALLOWED
            if len(request.json) == 0:
                return "{}", status.HTTP_400_BAD_REQUEST
            if request.json == None or key == request.json[0]:
                return "{}", status.HTTP_400_BAD_REQUEST
        data[request.json[0]] = []
        acts = open('acts.json', 'w')
        json.dump(data, acts)
        acts.close()
        return "{}", status.HTTP_201_CREATED

#5
@app.route('/cremove.html')
def cremove():
    return render_template('removeCat.html')

@app.route('/api/v1/categories/<categoryname>', methods = ["DELETE"])
def removeCategory(categoryname):
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    for key, value in data.items():
        if key == categoryname:
            r = []
            for value in data[key]:
                r.append(value['actId'])
            del data[key]
            acts = open('acts.json', 'w')
            json.dump(data, acts)
            acts.close()
            acts = open('actid.json')
            data = json.load(acts)
            acts.close()
            for i in r:
                data['ID'].remove(i)
            acts = open('actid.json', 'w')
            json.dump(data, acts)
            acts.close()
            return "{}", status.HTTP_200_OK
    return "{}", status.HTTP_400_BAD_REQUEST

#6
@app.route('/listact.html')
def listact():
    return render_template('listActs.html')

@app.route('/api/v1/categories/<categoryname>/acts', methods = ["GET"])
def listActs(categoryname):
    if len(request.args) == 2:
        return catRange(categoryname, int(request.args.get('start')), int(request.args.get('end')))
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    for key, value in data.items():
        if key == categoryname:
            if len(value) < 100:
                result = data[key]
                if result == []:
                    return "[]", status.HTTP_204_NO_CONTENT
                return json.dumps(result), status.HTTP_200_OK
            else:
                return "[]", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                #return ' '.join(str(i) for i in value)
    return "[]", status.HTTP_400_BAD_REQUEST

#7
@app.route('/size.html')
def size():
    return render_template("catSize.html")

@app.route('/api/v1/categories/<categoryname>/acts/size', methods = ["GET"])
def categorySize(categoryname):
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    for key, value in data.items():
        if key == categoryname:
            return json.dumps([len(value)]), status.HTTP_200_OK
    return "[]", status.HTTP_204_NO_CONTENT

#8
@app.route('/crange.html')
def crange():
    return render_template("catRange.html")

#@app.route('/api/v1/categories/<categoryname>/acts?start=<startRange>&end=<endRange>', methods = ["GET"])
def catRange(categoryname, startRange, endRange):
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    result = {}
    for key, value in data.items():
        if key == categoryname:
            if startRange < 1 or  endRange > len(value):
                return "[]", status.HTTP_400_BAD_REQUEST
            elif endRange - startRange + 1 > 100:
                return "[]", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            else:
                return json.dumps(data[key][startRange-1: endRange]), status.HTTP_200_OK
    return "[]", status.HTTP_204_NO_CONTENT

#9
@app.route('/api/v1/acts/upvote', methods = ["POST"])
def upvote():
    if request.method == "POST":
        actid = request.json[0]
        acts = open('acts.json')
        data = json.load(acts)
        acts.close()
        for key, value in data.items():
            for i in range(len(value)):
                if value[i]['actId'] == actid:
                    data[key][i]['upvotes'] += 1
                    acts = open('acts.json', 'w')
                    json.dump(data, acts)
                    acts.close()
                    return "{}", status.HTTP_200_OK
        return "{}", status.HTTP_400_BAD_REQUEST
    else:
        return "{}", status.HTTP_405_METHOD_NOT_ALLOWED

#10
@app.route('/api/v1/acts/<actid>', methods = ["DELETE"])
def removeAct(actid):
    if request.json == {} and actid != 'upvote':
        actid = int(actid)
        acts = open('acts.json')
        data = json.load(acts)
        acts.close()
        for key, value in data.items():
            for act in range(len(value)):
                if value[act]['actId'] == actid:
                    data[key].pop(act);
                    acts = open('acts.json', 'w')
                    json.dump(data, acts)
                    acts.close()
                    actsid = open('actid.json')
                    dataid = json.load(actsid)
                    actsid.close()
                    dataid['ID'].remove(actid)
                    actsid = open('actid.json', 'w')
                    json.dump(dataid, actsid)
                    actsid.close()
                    return "{}", status.HTTP_200_OK
        return "{}", status.HTTP_400_BAD_REQUEST
    else:
        return "{}",status.HTTP_405_METHOD_NOT_ALLOWED

#11
@app.route('/upload.html')
def upload():
    return render_template('upload.html')

@app.route('/api/v1/acts', methods = ["POST"])
def uploadAct():
    users = open('users.json')
    data = json.load(users)
    users.close()
    userlist = []
    for cred in data['credentials']:
        userlist.append(cred['username'])
    if request.json['username'] not in userlist:
        return "{}", status.HTTP_400_BAD_REQUEST
    ts = request.json['timestamp']
    if len(ts) == 19 and ts[2] == '-' and ts[5] == '-' and ts[10] == ':' and ts[13] == '-' and ts[16] == '-':
        pass;
    else:
        return "{}", status.HTTP_400_BAD_REQUEST
    try:
        base64.decodestring(str.encode(request.json['imgB64']))
    except binascii.Error:
        return "b64", status.HTTP_400_BAD_REQUEST
    if 'upvotes' in request.json.keys():
        return "{}", status.HTTP_400_BAD_REQUEST
    actid = open('actid.json')
    dataid = json.load(actid)
    actid.close()
    if request.json['actId'] in dataid['ID']:
        return "{}", status.HTTP_400_BAD_REQUEST
    dataid['ID'].append(request.json['actId'])
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    if request.json['categoryName'] not in data.keys():
        return "{}", status.HTTP_400_BAD_REQUEST
    request.json['upvotes'] = 0
    catname = request.json.pop('categoryName')
    data[catname] = [request.json] + data[catname]
    acts = open('acts.json', 'w')
    json.dump(data, acts)
    acts.close()
    actid = open('actid.json', 'w')
    json.dump(dataid, actid)
    actid.close()
    return "{}", status.HTTP_201_CREATED

if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug = True)
