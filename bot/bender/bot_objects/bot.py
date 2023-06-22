import os
from dotenv import load_dotenv

class Bot(object):
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('API_KEY')
        