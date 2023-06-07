'''
@File    :   WebsocketServer.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import asyncio
from websockets.exceptions import ConnectionClosed
import json 
import websockets
import json 

class Server:
    def __init__(self, host="192.168.2.11", port=8765):
        self.host_ = host
        self.port_ = port
        self.server_ = None
        self.vr_client_ = None
        self.mule_client_ = None
        self.rooms_ = []

    def parse_client_message(self, message):
        json_message = json.loads(message)
        return json_message
    
    async def unregister_(self, websocket):
        if self.vr_client_ == websocket:
            self.vr_client_ = None
        elif self.mule_client_ == websocket:
            self.mule_client_ = None
        else:
            print("[Error] Unknown client type!")
            return
        
    async def add_client_(self, websocket, message):
        print(f"Adding client: {message}")
        message = self.parse_client_message(message)
        if message['client_type'] == "VR":
            self.vr_client_ = websocket
        elif message['client_type'] == "MULE":
            self.mule_client_ = websocket
        else:
            print("[Error] Unknown client type!")
            return
    
    async def handle_message_(self, message, websocket):
        message = self.parse_client_message(message)
        
        if message['type'] == "join":
            await self.handle_join_(message)
        elif message['type'] == "set_client_type":
            if message['client_type'] == "VR":
                print(f"[INFO] Added VR client: {websocket}")
                self.vr_client_ = websocket
            elif message['client_type'] == "MULE":
                print(f"[INFO] Added MULE client: {websocket}")
                self.mule_client_ = websocket
        elif message['type'] == "offer":
            if self.vr_client_ is not None:
                await self.send_to_client_(self.vr_client_, json.dumps(message))
        elif message["type"] == "answer":
            if self.mule_client_ is not None:
                await self.send_to_client_(self.mule_client_, json.dumps(message))
        elif message["type"] == "candidate":
            if websocket == self.vr_client_:
                await self.send_to_client_(self.mule_client_, json.dumps(message))
            elif websocket == self.mule_client_:
                await self.send_to_client_(self.vr_client_, json.dumps(message))
                
    async def handle_join_(self, message):
        print(f"Handling join: {message}")
        if message['client_type'] == "MULE":
            self.rooms_.append(message['room'])
            print(f"Added room: {message['room']}")
        elif message['client_type'] == "VR":
            print(f"[INFO] Added VR client to room: {message['room']}")
            message = {
                "type": "ready",
                "room": message['room']
            }
            if self.mule_client_ is not None:
                print(f"[INFO] Sending ready message to MULE: {message}")
                await self.send_to_client_(self.mule_client_, json.dumps(message))
            else:
                print("[INFO] MULE not connected!")
                
    async def handler_(self, websocket, path):
        try:
            async for message in websocket:
                print(f"[INFO] Received message: {message}")
                await self.handle_message_(message, websocket)
                
        except ConnectionClosed:
            print("[Error] Client disconnected!")
            await self.unregister_(websocket)
        except Exception as e:
            print(f"[Error] {e}")
            await self.unregister_(websocket)
            
    async def send_to_client_(self, websocket, message):
        if websocket != self.vr_client_ and websocket != self.mule_client_:
            raise ValueError("Client not found")
        await websocket.send(message)
    
    async def send_to_peer_(self, websocket, message):
        if websocket == self.vr_client_:
            await self.send_to_client_(self.mule_client_, message)
        elif websocket == self.mule_client_:
            await self.send_to_client_(self.vr_client_, message)
        else:
            raise ValueError("[Error] Client not found")
        
    async def start(self):
        self.server_ = await websockets.serve(self.handler_, self.host_, self.port_)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.start())
        print(f"Server started at ws://{self.host_}:{self.port_}")
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    server = Server()
    server.run()
  
