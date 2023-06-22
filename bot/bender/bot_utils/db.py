import os
from dotenv import load_dotenv
import asyncpg

from bot_objects.community import Community

class DB(object):
    
    def __init__(self):
        load_dotenv()
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_PORT = os.getenv('DB_PORT')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USERNAME = os.getenv('DB_USERNAME')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        
    async def make_query(query_text: str, query_params):
        conn = await asyncpg.connect(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        if query_text.startswith('SELECT'):
            results = await conn.fetch(query_text, *query_params)
        else:
            results = None
        await conn.execute(query_text, *query_params)
        await conn.close()
        return results
    
    async def get_preys(prey_type, user_id=None, community: Community):
        if user_id is None:
            query = "SELECT id, name, text, user_id FROM bender_prey WHERE type = $1 AND user_id = $2 AND community_id = $3"
            params = (prey_type, user_id, community.id)
        else:
            query = "SELECT id, name, text, user_id FROM bender_prey WHERE type = $1 AND community_id = $2"
            params = (prey_type, community.id)
        return await make_query(query, params)