import sys, json 

try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
except ImportError:
    print("Error: aiortc is not installed!")
    sys.exit(1)
    
class JoinMessage:
    def __init__(self):
        self.type = ""
        self.room = ""
        self.name = ""
        self.client_type = ""
        
    def to_json(self):
        return json.dumps(self.__dict__)
    
class Message:
    def __init__(self):
        self.origin = ""
        self.type = ""
        self.data = ""
    def to_json(self):
        return json.dumps(self.__dict__)
    
class OfferMessage:
    def __init__(self):
        self.origin = ""
        self.type = ""
        self.sdp = ""
        self.room = ""
    
    def to_json(self):
        return json.dumps(self.__dict__)

class AnswerMessage:
    def __init__(self):
        self.origin = ""
        self.type = ""
        self.sdp = ""
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_json(json_str):
        try:
            json_dict = json.loads(json_str)
            origin = json_dict['origin']
            type = json_dict['type']
            sdp = json_dict['sdp']
            AnswerMessage = AnswerMessage()
            AnswerMessage.origin = origin
            AnswerMessage.type = type
            AnswerMessage.sdp = sdp
            return AnswerMessage
        except Exception as e:
            print(f"[ERROR] in creating answer from json with message: {e}")
            return None
                
class ClientTypeMessage:
    def __init__(self):
        self.type = ""
        self.client_type = ""
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
class CandidateMessage:
    def __init__(self):
        self.origin = ""
        self.type = ""
        self.candidate = ""
        self.sdpMid = ""
        self.sdpMLineIndex = 0
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_str(json_str):
        try:
            json_dict = json.loads(json_str)
            candidate = json_dict['candidate']
            return RTCIceCandidate(
                candidate['candidate'], 
                candidate['sdpMid'], candidate['sdpMLineIndex'])
        except Exception as e:
            print(f"[ERROR] in creating candidate from json with message: {e}")
            raise e