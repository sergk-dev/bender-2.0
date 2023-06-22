# docstring: Community class
import os
from dotenv import load_dotenv

from bot_objects.bot import Bot

class Community(object):
    
    _instance = None
    
    def __init__(self):
        load_dotenv()
        self.COMMUNITY_ID = os.getenv('COMMUNITY_ID')
        self.bot = Bot()
        self.id = self.COMMUNITY_ID
        
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Community, cls).__new__(cls)
        return cls._instance
    
    