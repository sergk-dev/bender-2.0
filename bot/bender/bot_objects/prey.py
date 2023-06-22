#...

from bot_objects.community import Community
from bot_utils.db import DB

class Prey(object):
    
    def __init__(self, prey_id: int, name: str, text: str, prey_type: str, user_id: int):
        self.prey_id = id
        self.name = name
        self.text = text
        self.prey_type = prey_type
        self.user_id = user_id
        self.community = Community()
        
    async def reread (self):
        db = DB()
        prey_row = await db.get_prey_by_id(self.prey_id)
        if prey_row is None:
            return None
        self.name = prey_row['name']
        self.text = prey_row['text']
        self.prey_type = prey_row['type']
        self.user_id = prey_row['user_id'] 
        return self
        