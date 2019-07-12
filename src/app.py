from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

from flask_socketio import SocketIO
from flask_socketio import send, emit

# from models import HttpMessage


DEBUG = True

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)
# db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template("base.html")


@app.route('/sock')
def sock():
    broadcast("hello")
    return "sock"


@socketio.on('connect')
def handle_connect():
    broadcast("Welcome")


@socketio.on('message')
def handle_message(message):
    print("MESSAGE RECEIVED============================")
    print(message)


def broadcast(data):
    socketio.emit('news', data)

# https://flask-socketio.readthedocs.io/en/latest/
# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))


# @socketio.on('my event')
# def handle_my_custom_event(json):
#     print('received json: ' + str(json))


if __name__ == '__main__':
    # if DEBUG:
    #     try:
    #         HttpMessage.HttpMessage.query.delete()  # Delete existing entries
    #     except OperationalError:
    #         db.create_all()  # Table not created yet
    socketio.run(app, port=8000, debug=DEBUG)
    # app.run(host="0.0.0.0", port="8000", debug=DEBUG)
