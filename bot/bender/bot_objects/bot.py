# Bot class

import os
from dotenv import load_dotenv

class Bot(object):
    
    _instance = None
    
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('API_KEY')
        
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
        return cls._instance
        