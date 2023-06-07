'''
@File    :   Client.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import sys 

try:
    import asyncio
    from socketio import AsyncClient
except ImportError:
    print("Error: asyncio is not installed!")
    sys.exit(1)

from Message import *
from PeerConnection import PeerConnection

class Client:
    def __init__(self, name=""):
        self.sio_ = AsyncClient()
        self.connected_ = False
        self.name_ = name
        
        # peer connections 
        self.peer_connection_ = None
        
        self.setup_()
    
    def set_name(self, name):
        self.name_ = name
        
    def setup_(self):
        self.sio_.on('connect', self.on_connect_)
        self.sio_.on('disconnect', self.on_disconnect_)
        self.sio_.on('message', self.on_message_)
        self.sio_.on('offer', self.on_offer_)
        self.sio_.on('answer', self.on_answer_)
        self.sio_.on('candidate', self.on_candidate_)
        self.sio_.on('client_connected', self.on_client_connected_)
    
    async def create_peer_connection(self):
        print("[INFO] creating peer connection...")
        self.peer_connection_ = PeerConnection()
        await self.peer_connection_.send_offer(self.sio_, self.room_)
        
    
    async def on_client_connected_(self, message):
        print(f"[INFO] client connected with message: {message}")
        await self.create_peer_connection()
        
    async def join(self, room):
        print(f"[INFO] joining room: {room}")
        message = JoinMessage()
        message.room = room
        message.name = self.name_
        message.type = "join"
        
        if self.connected_:
            await self.sio_.emit('mule_join', message.to_json())
            print("[INFO] joined room!")
            self.room_ = room
        else:
            print("[ERROR] not connected to server!")
        
    async def connect(self, url):
        print("[INFO] connecting to server...")
        await self.sio_.connect(url)
    
    async def disconnect(self):
        print("[INFO] disconnecting from server...")
        await self.sio_.disconnect()
    
    async def send(self, message : Message) -> None:
        await self.sio_.emit('message', message.to_json())
    
    async def on_connect_(self):
        print("[INFO] connected to server!")
        self.connected_ = True
    
    async def on_disconnect_(self):
        print("[INFO] disconnected from server!")
        self.connected_ = False
        
    
    async def on_message_(self, message):
        print(f"[INFO] received message: {message}")
    
    async def on_offer_(self, message):
        print(f"[INFO] received offer: {message}")
    
    async def on_answer_(self, message):
        print(f"[INFO] received answer: {message}")
        message = json.loads(message)
        remote_description = RTCSessionDescription(
            sdp = message["sdp"],
            type = "answer"
        )
        print("[INFO] setting remote description from answer...")
        try:
            await self.peer_connection_.set_remote_description(remote_description)     
            print("[INFO] set remote description from answer!")   
        except Exception as e:
            print(f"[ERROR] in setting the remote description from answer with message {e}")
            
    async def on_candidate_(self, message):
        await self.peer_connection_.add_remote_candidate(message)
        

    async def run(self, url, room):
        await self.connect(url)
        await self.join(room)
        await self.sio_.wait()

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Mule client")
    parser.add_argument("--name", help="name of the client", default="mule01")
    parser.add_argument("--ip", help="ip of the server", default="127.0.0.1")
    parser.add_argument("--port", help="port of the server", default="9000")
    parser.add_argument("--room", help="room to join", default="test")
    
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    try:
        client = Client(args.name)
        url = f"http://{args.ip}:{args.port}"
        loop.run_until_complete(client.run(url, args.room))
    except KeyboardInterrupt:
        client.disconnect()
    finally:
        loop.run_until_complete(client.disconnect())
        loop.close()