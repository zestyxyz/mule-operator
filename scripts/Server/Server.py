'''
@File    :   Server.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import sys 
try:
    from flask import Flask, request 
    from flask_socketio import SocketIO, join_room
    from flask_cors import CORS
    
except ImportError:
    print("Error: Flask-SocketIO is not installed!")
    sys.exit(1)
    
from Room import Room 
import json 

class Server:
    def __init__(self):
        self.app_ = Flask(__name__)
        CORS(self.app_)
        self.app_.secret_key = 'secret'
        self.socket_ = SocketIO(self.app_, cors_allowed_origins="*")
        self.setup_()

        self.rooms_ = []
        
    def setup_(self):
        """
        Setup callback functions
        """
        
        self.socket_.on_event('connect', self.on_connect_)
        self.socket_.on_event('disconnect', self.on_disconnect_)
        self.socket_.on_event('message', self.on_message_)
        
        self.socket_.on_event('offer', self.on_offer_)
        self.socket_.on_event('answer', self.on_answer_)
        self.socket_.on_event('candidate', self.on_candidate_)
        
        self.socket_.on_event('join', self.on_join_)
        self.socket_.on_event('leave', self.on_leave_)
        self.socket_.on_event('close', self.on_close_)
        self.socket_.on_event('error', self.on_error_)
        self.socket_.on_event('mule_join', self.on_mule_join_)        
    
    def on_connect_(self):
        print("[INFO] client connected!")
    
    def on_disconnect_(self):
        print("[INFO] client disconnected!")
    
    def on_message_(self, message):
        print(f"[INFO] received message: {message}")
    
    def on_offer_(self, message):
        print(f"[INFO] received offer: {message}")
        room = message['room']
        print(f"[INFO] sending offer to Room {room}")
        self.socket_.emit('offer', message, to=room, skip_sid=request.sid)
    
    def on_answer_(self, message):
        print(f"[INFO] received answer: {message}")
        room = message['room']
        print(f"[INFO] sending answer to Room {room}")
        self.socket_.emit('answer', json.dumps(message), to=room, skip_sid=request.sid)
    
    def on_candidate_(self, message):
        print(f"[INFO] received candidate: {message}")
        room = message['room']
        print(f"[INFO] sending candidate to Room {room}")
        self.socket_.emit('candidate', json.dumps(message), to=room, skip_sid=request.sid)
    
    def on_join_(self, message) -> None:
        print(f"[INFO] received join: {message}")
        for room in self.rooms_:
            if room.get_name() == message['room']:
                room.add_vr_client(message['name'])
                join_room(room.get_name())
                print(f'[INFO] {message["name"]} joined {room.get_name()}')
                self.send_ready_(room.get_name())
                return
        self.send_cant_join()
        return 
        
    def on_mule_join_(self, message):
        print(f"[INFO] received mule join: {message}")
        message = json.loads(message)
        join_room(message['room'])
        self.rooms_.append(Room(message['room']))
        print(f"[INFO] created room: {message['room']}")
        
    def on_leave_(self, message):
        print(f"[INFO] received leave: {message}")
    
    def send_ready_(self, room):
        print(f"[INFO] sending ready to Room {room}")
        message = { 'username': 'vr-client'}
        self.socket_.emit('client_connected', message, to=room)
    
    def send_cant_join(self):
        message = { 'message': 'Room does not exist!'}
        self.socket_.emit('cant_join', json.dumps(message), to=request.sid)
    
    def on_close_(self, message):
        print(f"[INFO] received close: {message}")
    
    def on_error_(self, message):
        print(f"[INFO] received error: {message}")
    
    @property
    def app(self):
        return self.app_


if __name__ == '__main__':
    server = Server()
    server.socket_.run(server.app, host='0.0.0.0', port=9000, debug=False)