from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)

users = {}  # {username: sid}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    session['username'] = username
    users[username] = None  # سيتم تحديثه عند الاتصال
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('chat.html', username=session['username'])

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        username = session['username']
        users[username] = request.sid  # التخزين الصحيح لـ SID
        print(f"{username} connected with SID: {request.sid}")

@socketio.on('private_message')
def handle_private_message(data):
    recipient = data['recipient']
    message = data['message']
    sender = session['username']
    
    if recipient in users and users[recipient]:
        emit('new_message', {
            'sender': sender,
            'message': message
        }, room=users[recipient])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)