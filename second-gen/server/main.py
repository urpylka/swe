#! /usr/bin/env python3

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
# from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import psycopg2, datetime
from functools import wraps
# from db_models import Serializer, Role, Tag, Session, User, Post

app = Flask(__name__)
# https://pythonru.com/uroki/14-sozdanie-baz-dannyh-vo-flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:example@localhost:5432/postgres'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Serializer(object):
    '''
    Source:
    https://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask

    Use:
    def get_user(id):
        user = UserModel.query.get(id)
        return json.dumps(user.serialize())

    def get_users():
        users = UserModel.query.all()
        return json.dumps(UserModel.serialize_list(users))
    '''
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

roles_users = db.Table('roles_users',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    # A comma separated list of strings
    permissions = db.Column(db.UnicodeText, nullable=True)
    update_datetime = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.datetime.utcnow,
    )

class User(db.Model, Serializer):
    __tablename__ = 'user'

    id = db.Column(db.Integer, db.Sequence('users_id_seq', start=1, increment=1), primary_key = True, autoincrement=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    # Username is important since shouldn't expose email to other users in most cases.
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(64), unique=True, nullable=False)
    active = db.Column(db.Boolean(), nullable=False)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # один ко многим
    sessions = db.relationship('Session', backref='user', lazy='dynamic')

    def serialize(self):
        d = Serializer.serialize(self)
        del d['password_hash']
        return d

    # def __repr__(self):
    #     return self.serialize()

    def __init__(self, name, email, role, password):
        self.username = name
        self.email = email
        self.role = role
        self.password_hash = password

class Session(db.Model):
    __tablename__ = 'session'
    token = db.Column(db.Integer, primary_key = True)
    issued_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    expires_at = db.Column(db.DateTime) # +3650 nullable=False
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

# class Tag(db.Model):
#     __tablename__ = 'tags'
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(50))
#     # нужно реализовать один ко многим связь с PostsModel

# class Post(db.Model):
#     __tablename__ = 'posts'
#     id = db.Column(db.Integer, primary_key = True)
#     title = db.Column(db.String(50))
#     preview = db.Column(db.String(50))
#     text = db.Column(db.String(50))
#     created_at = db.Column(db.DateTime)
#     author = db.Column(db.Integer(), db.ForeignKey('users.id'))


def token_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # Getting token from HTTP header
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({"message":"Token is missing!" + str(token)}), 401

        try:
            # Taking session by token
            session = Session.query.filter_by(token=token).one()
            if not session:
                return jsonify({'message': 'Token is invalid 1!' + str(token)}), 401
        except Exception as ex:
            return jsonify({'message': 'Token is invalid 2!' + str(token), 'error':str(ex)}), 401

            # Check session
            if session.expired_at > datetime.now():
                return jsonify({"message":"Token expired!"}), 401
            else:
                current_user = session.user

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/v1/account', methods=['GET'])
@token_auth
def temp():
    return jsonify({"message": "This is temp callback. It will consist: login (basic), auth (token / session cookie), logout, reset, register, verify, 2fa-sms, 2fa-app, oauth, remember_me, capcha, role-model (permisions), safety pass keeping"}), 500

@app.route('/api/v1/users', methods=['GET'])
def user_showall():
    # https://medium.com/@erdoganyesil/typeerror-object-of-type-is-not-json-serializable-6230ccc74975
    try:
        users = User.query.all()
        users = User.serialize_list(users)
        return jsonify(users), 200
    except Exception as ex:
        return jsonify({"message": str(ex)}), 500

@app.route('/api/v1/users/<int:id>', methods=['GET'])
def user_show(id):
    user = User.query.filter_by(id = id).first()
    if user == None:
        user = {"message":"No user found by the id"}
        return jsonify(user), 404
    else:
        user = user.serialize()
        return jsonify(user), 200

@app.route('/api/v1/users', methods=['POST'])
def user_create():
    # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
    try:
        new_user = User(\
            request.args.get("name", ''), \
            request.args.get("email", ''), \
            request.args.get("role", ''), \
            request.args.get("password", ''))
    except Exception as ex:
        if str(ex).startswith("400 Bad Request"):
            return jsonify({"message": "400 Bad Request"}), 400
        else:
            return jsonify({"message": str(ex)}), 500

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        db.session.flush()
        if str(ex).startswith("(psycopg2.errors.UniqueViolation)"):
            return jsonify({"message":"Error: Some value is not unique"}), 400
        if str(ex).startswith("(psycopg2.errors.NotNullViolation)"):
            return jsonify({"message":"Error: Some value is null"}), 400
        return jsonify({"message":str(ex)}), 500

    user = User.query.filter_by(id = new_user.id).first()
    user = user.serialize()
    return jsonify(data), 201

@app.route('/api/v1/users/<int:id>', methods=['PUT'])
def user_update(id):
    try:
        user = User.query.filter_by(id = id).first()
        user.name = request.args.get("name", '')
        user.email = request.args.get("email", '')
        db.session.add(user)
        db.session.commit()

        data = User.query.filter_by(id = id).first()
        return jsonify(data), 200
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({"message":"ID does not exist"}), 404

@app.route('/api/v1/users/<int:id>', methods=['DELETE'])
def user_delete(id):
    try:
        User.query.filter_by(id = id).delete()
        db.session.commit()
        return jsonify({"message":"User was removed"}), 201
    except:
        db.session.rollback()
        db.session.flush()
        return jsonify({"message":"ID does not exist"}), 404

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.debug = True  # enables auto reload during development
    app.run()
