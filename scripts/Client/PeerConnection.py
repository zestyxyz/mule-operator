'''
@File    :   PeerConnection.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import sys 
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
except ImportError:
    print("Error: aiortc is not installed!")
    sys.exit(1)
    
from Message import *
from MediaTrack import MediaTrack

class PeerConnection:
    def __init__(self):
        config = RTCConfiguration()
        config.iceServers = [
            RTCIceServer(urls="stun:openrelay.metered.ca:80"),
            RTCIceServer(
                urls="turn:openrelay.metered.ca:80",
                username="openrelayproject",
                credential="openrelayproject"),
            RTCIceServer(
                urls="turn:openrelay.metered.ca:443",
                username="openrelayproject",
                credential="openrelayproject"),
            RTCIceServer(
                urls="turn:openrelay.metered.ca:443?transport=tcp",
                username="openrelayproject",
                credential="openrelayproject"),
        ]
        self.pc_ = RTCPeerConnection()
        self.setup_()
    
    def add_data_channel_(self, label):
        print(f"[INFO] creating data channel with label: {label}")
        self.data_channel_ = self.pc_.createDataChannel(label)
        self.data_channel_.on('message', self.on_data_channel_message_)     
        self.data_channel_ .on('open', self.on_data_channel_open_)
        self.data_channel_ .on('close', self.on_data_channel_close_)
        self.data_channel_ .on('error', self.on_data_channel_error_)
             
    def add_video_track_(self):
        print(f"[INFO] creating video track ... ")
        self.track_ = MediaTrack()
        self.pc_.addTrack(self.track_)
        
    def setup_(self):
        self.add_data_channel_("data")
        self.add_video_track_()
        self.pc_.on('iceconnectionstatechange', self.on_ice_connection_state_change_)
        self.pc_.on('icecandidate', self.on_ice_candidate_)
        self.pc_.on('connectionstatechange', self.on_connection_state_change_)
        self.pc_.on('signalingstatechange', self.on_signaling_state_change_)
        
    
    def on_data_channel_message_(self, message):
        print(f"[INFO] data channel message: {message}")
    
    def on_data_channel_open_(self):
        print(f"[INFO] data channel open")
    
    def on_data_channel_close_(self):
        print(f"[INFO] data channel close")
    
    def on_data_channel_error_(self, error):
        print(f"[ERROR] data channel error: {error}")
        
    def on_ice_connection_state_change_(self):
        print(f"[INFO] ice connection state changed to {self.pc_.iceConnectionState}")
    
    def parse_ice_message_(self, message):
        import re
        message = json.loads(message)
        candidate_str = message["candidate"]
        pattern = re.compile('candidate:(\d+) (\d+) (\S+) (\d+) (\S+) (\d+) typ (\S+)(?: raddr (\S+) rport (\d+))?(?: generation (\d+))?(?: ufrag (\S+))?(?: network-cost (\d+))?')
        m = pattern.match(candidate_str)
        if m:
            groups = m.groups()
            
            candidate = RTCIceCandidate(
                component=int(groups[1]),
                foundation=groups[0],
                protocol=groups[2],
                priority=int(groups[3]),
                ip=groups[4],
                port=int(groups[5]),
                type=groups[6],
                sdpMid=message["sdpMid"],
                sdpMLineIndex=int(message["sdpMLineIndex"]),
            )
            return candidate
        else:
            print("[ERROR] could not parse ice candidate!")
            return None
        
    # async def add_remote_candidate(self, message):
    #     message = json.loads(message)["candidate"]
    #     print(f"[INFO] received candidate: {message}")
    #     candidate = self.parse_ice_message_(message)
    #     if candidate:
    #         print(f"[INFO] adding candidate: {candidate}")
    #         try:
    #             await self.pc_.addIceCandidate(candidate)
    #             print("[INFO] candidate added successfully!")
    #         except Exception as e:
    #             raise Exception(e)
    #     else:
    #         print("[ERROR] candidate is None!")
            
    async def add_remote_candidate(self, message):
        print(f"[INFO] received candidate: {message}")
        candidate = self.parse_ice_message_(message)
        if candidate:
            print(f"[INFO] adding candidate: {candidate}")
            try:
                await self.pc_.addIceCandidate(candidate)
                print("[INFO] candidate added successfully!")
            except Exception as e:
                raise Exception(e)
        else:
            print("[ERROR] candidate is None!")
    
    async def on_ice_candidate_(self, event):
        if event.candidate:
            print(f"[INFO] ice candidate: {event.candidate}")
        else:
            print("[INFO] ice candidate is None!")
            
    def on_connection_state_change_(self):
        print(f"[INFO] connection state changed to {self.pc_.connectionState}")
    
    def on_signaling_state_change_(self):
        print(f"[INFO] signaling state changed to {self.pc_.signalingState}")
        
    
    async def create_offer(self) -> RTCSessionDescription:
        print("[INFO] sending offer")
        offer = await self.pc_.createOffer()
        if offer:
            await self.on_offer_created_(offer)
            return offer
        else:
            print("[ERROR] offer is None!")
            return None
    
    async def set_local_description(self, sdp):
        print("[INFO] setting local description")
        await self.pc_.setLocalDescription(sdp)
        
    async def on_offer_created_(self, description : RTCSessionDescription):
        print(f"[INFO] offer created: {description}")
        await self.set_local_description(description)
        
    async def send_offer(self, sio, room):
        offer = await self.create_offer()
        if offer:
            message = OfferMessage()
            message.type = "offer"
            message.sdp = offer.sdp
            message.origin = "mule"
            message.room = room
            print(f"[INFO] sending offer ... ")
            try:
                # await sio.emit('offer', message.to_json())
                await sio.send(message.to_json())
                print("[INFO] offer sent!")
            except Exception as e:
                print(f"[ERROR] error in sending offer: {e}")
                return
    
    async def set_remote_description(self, sdp):
        print(sdp)
        print("[INFO] setting remote description")
        try:
            await self.pc_.setRemoteDescription(sdp)
        except Exception as e:
            print(e)
        