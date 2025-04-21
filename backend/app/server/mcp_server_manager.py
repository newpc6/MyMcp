from multiprocessing import Manager
from multiprocessing.managers import BaseManager
from multiprocessing.connection import Connection
from app.utils.logging import em_logger


class McpServerManager(BaseManager):
    pass


class McpManagerServer(object):
    """
    队列服务器
    """
    def __init__(self, ip="0.0.0.0", port=50002):
        self.ip = ip
        self.port = port
        self.my_manager = McpServerManager(
                address=(str(self.ip), int(self.port))
                # , authkey=self.authkey
            )
        
    def run(self):
        self.my_manager.start()
    
    def register(self, name, cls):
        self.my_manager.register(name, cls)


class McpManagerClient(object):
    def __init__(self, ip="127.0.0.1", port=50002):
        self.ip = ip
        self.port = port
        self.my_manager = McpServerManager(
            address=(str(self.ip), int(self.port))
        )
    
    def connect(self):
        self.my_manager.connect()

    def get_register_object(self, obj):
        if hasattr(self.my_manager, 'obj'):
            return self.my_manager.obj
        else:
            return None
