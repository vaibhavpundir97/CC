from flask import Flask, render_template, request
from flask_api import status
import json
import time
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
                return "Username exists!!!", status.HTTP_400_BAD_REQUEST
        users = open('users.json', 'w')
        data['credentials'].append(request.json)
        json.dump(data, users)
        users.close()
        return "Success", status.HTTP_201_CREATED

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
                return "Success", status.HTTP_200_OK
        return "User doesn't exist", status.HTTP_400_BAD_REQUEST

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
            return "No Content", status.HTTP_204_NO_CONTENT
        return render_template("categories.html", result = result), status.HTTP_200_OK
    else:
        for key, value in data.items():
            if key == request.json[0]:
                return "Category already exists", status.HTTP_400_BAD_REQUEST
        data[request.json[0]] = []
        acts = open('acts.json', 'w')
        json.dump(data, acts)
        acts.close()
        return "Success", status.HTTP_201_CREATED

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
            del data[key]
            acts = open('acts.json', 'w')
            json.dump(data, acts)
            acts.close()
            return "Success", status.HTTP_200_OK
    return "Category name doesn't exist", status.HTTP_400_BAD_REQUEST

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
                    return "No Content", status.HTTP_204_NO_CONTENT
                return render_template("listActsCat.html", result = result), status.HTTP_200_OK
            else:
                return "Too Large", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                #return ' '.join(str(i) for i in value)
    return "Category not present", status.HTTP_400_BAD_REQUEST

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
            return str(len(value)), status.HTTP_200_OK
    return "Category not present", status.HTTP_204_NO_CONTENT

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
                return "Out of Range", status.HTTP_204_NO_CONTENT
            elif endRange - startRange + 1 > 100:
                return "Too many Acts", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            else:
                return render_template('listActsCat.html', result = data[key][startRange-1: endRange]), status.HTTP_200_OK
    return "Category does not exist", status.HTTP_204_NO_CONTENT
#9
@app.route('/api/v1/acts/upvote', methods = ["POST"])
def upvote():
    actid = int(request.json[0])
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
                return "Success", status.HTTP_200_OK
    return "Wrong ActId", status.HTTP_400_BAD_REQUEST

#10
@app.route('/api/v1/acts/<actid>', methods = ["DELETE"])
def removeAct(actid):
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
                return "Success", status.HTTP_200_OK
    return "Not Found", status.HTTP_400_BAD_REQUEST

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
        return "Username not present", status.HTTP_400_BAD_REQUEST
    actid = open('actid.json')
    dataid = json.load(actid)
    actid.close()
    if request.json['actId'] in dataid['ID']:
        return "Id not unique", status.HTTP_400_BAD_REQUEST
    dataid['ID'].append(request.json['actId'])
    acts = open('acts.json')
    data = json.load(acts)
    acts.close()
    if request.json['categoryName'] not in data.keys():
        return "Category not present", status.HTTP_400_BAD_REQUEST
    request.json['upvotes'] = 0
    catname = request.json.pop('categoryName')
    data[catname] = [request.json] + data[catname]
    acts = open('acts.json', 'w')
    json.dump(data, acts)
    acts.close()
    actid = open('actid.json', 'w')
    json.dump(dataid, actid)
    actid.close()
    return "Success", status.HTTP_201_CREATED

if __name__ == '__main__':
   app.run(host = '0.0.0.0', debug = True)
