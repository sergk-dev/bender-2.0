#...

from bot_objects.community import Community
from bot_utils.db import DB

class Prey(object):
    
    def __init__(self, prey_id: int, name: str, text: str, prey_type: str, user_id: int):
        self.prey_id = prey_id
        self.name = name
        self.text = text
        self.prey_type = prey_type
        self.user_id = user_id
        self.community = Community()
        self.db = DB()
        
    async def reread (self):
        prey_row = await self.db.get_prey_by_id(self.prey_id)
        if prey_row is None:
            return None
        self.name = prey_row['name']
        self.text = prey_row['text']
        self.prey_type = prey_row['type']
        self.user_id = prey_row['user_id'] 
        return self
    
    @classmethod
    async def get_prey_by_id(cls, prey_id:int):
        db = DB()
        prey_row = await db.get_prey_by_id(prey_id)
        if prey_row is None:
            return None
        return Prey(
                prey_id=prey_row['prey_id'],
                name=prey_row['name'],
                text=prey_row['text'],
                prey_type=prey_row['prey_type'],
                user_id=prey_row['user_id']
            )
    
        