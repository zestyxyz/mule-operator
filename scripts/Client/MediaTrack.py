'''
@File    :   MediaTrack.py
@Time    :   2023/05/31
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

import sys
try:
    from aiortc import MediaStreamTrack, VideoStreamTrack
except ImportError:
    print("Error: aiortc is not installed!")
    sys.exit(1)

try:
    from av import VideoFrame
except ImportError:
    print("Error: av is not installed!")
    sys.exit(1)

import cv2 
import numpy as np

class MediaTrack(VideoStreamTrack):
    kind = "video"
    def __init__(self):
        super().__init__()
        self.cap_ = cv2.VideoCapture(0)
        if not self.cap_.isOpened(): 
            print("[Error] Could not open video device")
        else:
            print("[INFO] Video device opened")
            
        self.cap_.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap_.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap_.set(cv2.CAP_PROP_FPS, 30)
        
    async def recv(self):
        try:
            return await self.send_webcam_frame()
        except Exception as e:
            print(f"[Error] in sending frame with message {e}")
        
    
    async def create_random_frame(self):
        try:
            pts, time_base = await self.next_timestamp()
            frame = np.random.randint(0, 255, size=(480, 640, 3), dtype=np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = VideoFrame.from_ndarray(frame, format="rgb24")
            frame.pts = pts
            frame.time_base = time_base
            return frame
        except Exception as e:
            raise Exception(f"[Error] in creating random frame with message {e}")
    
    async def send_webcam_frame(self):
        try:
            pts, time_base = await self.next_timestamp()
            ret, frame = self.cap_.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = VideoFrame.from_ndarray(frame, format="rgb24")
            frame.pts = pts
            frame.time_base = time_base
            return frame
        except Exception as e:
            raise Exception(f"[Error] in sending webcam frame with message {e}")
    