
from flask import Flask, jsonify
from chatup_chat.api.admin import Admin
from chatup_chat.api.customer import Customer
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
socketio.on_namespace(Customer('/customer'))
socketio.on_namespace(Admin('/admin'))


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status='healthy'), 200


@app.route('/', methods=['GET'])
def health():
    return jsonify(status='healthy'), 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8014)
