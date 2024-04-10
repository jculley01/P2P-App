from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit
import hashlib

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}

@socketio.on('register')
def handle_register(data):
    username = data['username']
    session_id = request.sid
    clients[username] = {
        'session_id': session_id,
        'online': True,
        'messages': []
    }
    join_room(username)
    emit('registration_response', {'message': f'{username} registered successfully', 'status': 'success'})
    update_peers()

@socketio.on('unregister')
def handle_unregister(data):
    username = data['username']
    if username in clients:
        leave_room(username)
        clients[username]['online'] = False
        emit('unregistration_response', {'message': f'{username} unregistered successfully', 'status': 'success'})
        update_peers()

def update_peers():
    online_users = {user: {"online": clients[user]['online']} for user in clients if clients[user]['online']}
    emit('update_peers', online_users, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    sender = data['from']
    receiver = data['to']
    content = data['content']
    hashed_content = hashlib.sha256(content.encode()).hexdigest()

    if receiver in clients and clients[receiver]['online']:
        emit('receive_message', {'from': sender, 'content': hashed_content}, room=clients[receiver]['session_id'])
    elif receiver in clients:
        clients[receiver]['messages'].append({'from': sender, 'content': hashed_content})
        emit('message_status', {'message': 'Message stored for offline user', 'status': 'success'})
    else:
        emit('message_status', {'message': 'Receiver not found', 'status': 'error'})

@socketio.on('connect')
def on_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected:', request.sid)
    # Optionally handle user disconnects to toggle their online status
    for username, info in clients.items():
        if info['session_id'] == request.sid:
            info['online'] = False
            update_peers()
            break

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
