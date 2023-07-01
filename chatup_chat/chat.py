
from flask import Flask
from chatup_chat.api.customer import Customer
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
socketio.on_namespace(Customer('/customer'))


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8014)
