'''
@File    :   Room.py
@Time    :   2023/05/30
@Author  :   Armin Sadeghi 
@Version :   0.1
@Contact :   armin@zesty.xyz
@Desc    :   None
'''

class Room:
    def __init__(self, name):
        self.name_ = name
        self.mule_ = None
        self.vr_clients_ = []
        
    def get_name(self):
        return self.name_
    
    def get_mule(self):
        return self.mule_
    
    def add_vr_client(self, client):
        self.vr_clients_.append(client)
        
    def get_vr_clients(self):
        return self.vr_clients_
    
    def __str__(self) -> str:
        return f"Room: {self.name_}"
