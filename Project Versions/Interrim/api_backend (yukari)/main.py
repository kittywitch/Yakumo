from flask import Flask, request, jsonify, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json, os, uuid, datetime, hashlib, platform

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yakumo.db'
app.config['UPLOAD_FOLDER'] = "./files"
db = SQLAlchemy(app)

def creation_date(filepath):
    if platform.system() == 'Windows':
        return os.path.getctime(filepath)
    else:
        stat = os.stat(filepath)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    realname = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(), unique=False, nullable=False)
    avatarurl = db.Column(db.String(120), unique=False, nullable=False)
    channels = db.Column(db.String(), unique=False, nullable=True)
    tokens = db.relationship('Token', backref="user", lazy=True)

    def __repr__(self):
        return json.dumps({
            "username":self.username,
            "realname":self.realname,
            "avatar":self.avatarurl,
            "channels":self.channels.split(",")
        })

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(), nullable=False)
    last_used = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    channel = db.Column(db.String())
    message = db.Column(db.String())
    timestamp = db.Column(db.Integer)
            
@app.route('/api/add_message', methods=['POST'])
def add_message():
    if request.method == 'POST':
        content = request.json
        new_message = Message(message=content["message"], channel=content["channel"], timestamp=content["timestamp"], username=content["username"])
        db.session.add(new_message)
        db.session.commit()
        return json.dumps({
            "action":"message_upload",
            "status":"successful"
        })

@app.route('/api/uploads', methods=['POST'])
def uploads():
    if request.method == 'POST':
        content = request.json
        token = Token.query.filter_by(token=content["token"]).first()
        user_from_token = User.query.filter_by(id=token.user_id).first()
        upload_list = []
        for filename in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], f"./{user_from_token.username}")):
            full_name = os.path.join(app.config['UPLOAD_FOLDER'], f"./{user_from_token.username}/{filename}")
            filetime = int(creation_date(full_name))
            url = url_for('uploaded_file', username=user_from_token.username, filename=filename)
            upload_list.append({"time":filetime,"url":url})
            
        return json.dumps({
            "action":"upload_list", 
            "status":"successful", 
            "uploads":upload_list
        })

@app.route('/api/auth/login', methods=['POST'])
def login():
    # to-do: generate uuid token and store it in DB for session checking
    if request.method == 'POST':
        content = request.json
        if "password" in content and "username" in content and "token" not in content:
            found_user = User.query.filter_by(username=content["username"]).first()
            if found_user.password == content["password"]:
                raw_token = str(uuid.uuid4())
                token = Token(token=raw_token, last_used=int(datetime.datetime.utcnow().timestamp()), user_id=found_user.id)
                db.session.add(token)
                db.session.commit()
                return json.dumps({
                    "action":"auth",
                    "status":"successful",
                    "user":repr(found_user),
                    "token":raw_token
                })
        elif "token" in content:
            token = Token.query.filter_by(token=content["token"]).first()
            user_from_token = User.query.filter_by(id=token.user_id).first()
            token.last_used = int(datetime.datetime.utcnow().timestamp())
            db.session.commit()     
            return json.dumps({
                "action":"auth",
                "status":"successful",
                "user":repr(user_from_token),
                "token":content["token"]
            })
        else:
            return json.dumps({
                "action":"auth",
                "status":"failure"
            })

def generate_failure(action, reason):
    return json.dumps({
        "action":action,
        "status":"failure",
        "reason":reason
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    # to-do: generate uuid token and store it in DB for session checking
    if request.method == 'POST':
        content = request.json
        if "password" in content and "username" in content and "realname" in content:
            if len(content["username"]) < 3:
                return generate_failure("register", "Username must be at least 3 characters.")
            if len(content["password"]) < 8:
                return generate_failure("register", "Password must be at least 8 characters.")
            user_check = User.query.filter_by(username=content["username"]).first()
            if not user_check:
                if "username" in content and "password" in content:
                    new_user = User(username=content["username"], password=content["password"], avatarurl="", realname=content["realname"], channels="#lobby")
                    db.session.add(new_user)
                    db.session.commit()
                    raw_token = str(uuid.uuid4())
                    token = Token(token=raw_token, last_used=int(datetime.datetime.utcnow().timestamp()), user_id=new_user.id)
                    db.session.add(token)
                    db.session.commit()
                    return json.dumps({
                        "action":"register",
                        "status":"success",
                        "user":repr(new_user),
                        "token":raw_token
                    })
            else:
                return generate_failure("register", "User with the username provided already exists.")
        else:
            return generate_failure("register", "No username, realname and/or password provided.")

@app.route('/uploads/<username>/<filename>')
def uploaded_file(username, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], f"./{username}"),
                               filename)
                               
@app.route('/api/upload', methods=['POST'])
def upload():
    # to-do: add user checks and auth to this
    if request.method == 'POST' and "token" in request.form:
        file = request.files['upload_file']
        token = request.form['token']
        token_obj = Token.query.filter_by(token=token).first()
        user_from_token = User.query.filter_by(id=token_obj.user_id).first()
        ext = file.filename.split(".")[1]
        filename = "yakumo-" + str(uuid.uuid4()) + "." + ext
        user_path = os.path.join(app.config['UPLOAD_FOLDER'], f"./{user_from_token.username}")
        print(user_path)
        print("hello")
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        file.save(os.path.join(user_path, filename))
        return json.dumps({"url":url_for('uploaded_file', username=user_from_token.username, filename=filename), "status":"successful"})
    else:
        return '',401

def bootstrap():
    db.create_all()
    m = hashlib.sha256()
    m.update("testy".encode("utf-8"))
    test = User(username='test', realname="tester", avatarurl="heh", password=m.hexdigest(), channels="#lobby,#test")
    db.session.add(test)
    db.session.commit()

bootstrap()

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)
