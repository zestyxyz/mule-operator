'''
@File    :   WebsocketClient.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import sys 
import websockets
from websockets.exceptions import ConnectionClosed
try:
    import asyncio
except ImportError:
    print("Error: asyncio is not installed!")
    sys.exit(1)

from Message import *
from PeerConnection import PeerConnection

class Client:
    client_type = "MULE"
    room = "test"
    name = "mule"
    def __init__(self, host="192.168.2.11", port=8765):
        self.connected_ = False
        self.uri_ = f"ws://{host}:{port}"
        self.socket_ = None
        
        # peer connections 
        self.peer_connection_ = None
    
    async def connect(self):
        self.socket_  = await websockets.connect(self.uri_) 
        self.connected_ = True
        await self.send_client_type_()
        print("[INFO] connected to server!")
        await self.send_join_()
    
    async def send_client_type_(self):
        message = ClientTypeMessage()
        message.type = "set_client_type"
        message.client_type = Client.client_type
        message = message.to_json()
        print(f"[INFO] sending client type message: {message}")
        await self.socket_.send(message)
        
    async def disconnect(self):
        if self.socket_ is None:
            return
        
        print("[INFO] disconnecting from server...")
        await self.socket_.close()
        self.connected_ = False
        print("[INFO] disconnected from server!")
    
    async def handle_message(self):
        while self.connected_:
            try:
                message = await self.socket_.recv()
                print(f"[INFO] received message: {message}")
                
                await self.parse_message_(message)
                
            except ConnectionClosed:
                print("[ERROR] connection closed!")
                self.connected_ = False
            except Exception as e:
                print(f"[ERROR] {e}")
    
    async def send_join_(self):
        message = JoinMessage()
        message.room = Client.room
        message.name = Client.name
        message.type = "join"
        message.client_type = Client.client_type
        message = message.to_json()
        print(f"[INFO] sending join message: {message}")
        await self.socket_.send(message)
        
    async def handle_vr_connected_(self, message):
        print("[INFO] vr connected!")
        await self.create_peer_connection()
    
    async def on_answer_(self, message):
        print("=========")
        print(f"[INFO] received answer: {message}")

        
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
            
    async def parse_message_(self, message):
        json_message = json.loads(message)
        if json_message['type'] == "answer":
            print("[INFO] received answer!")
            await self.on_answer_(json_message)
        elif json_message['type'] == "candidate":
            await self.peer_connection_.add_remote_candidate(message)
        elif json_message['type'] == "ready":
            await self.handle_vr_connected_(json_message)
            
    def set_name(self, name):
        self.name_ = name
          
    async def create_peer_connection(self):
        print("[INFO] creating peer connection...")
        self.peer_connection_ = PeerConnection()
        await self.peer_connection_.send_offer(self.socket_, Client.room)
        
    
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
    
        

    async def run(self):
        await self.connect()
        await self.handle_message()
        
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
        client = Client()
        loop.run_until_complete(client.run())
    except KeyboardInterrupt:
        client.disconnect()
    finally:
        loop.run_until_complete(client.disconnect())
        loop.close()