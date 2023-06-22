import os
from typing import Union

from dotenv import load_dotenv
import asyncpg

from bot_objects.community import Community
from bot_objects.prey import Prey


class DB(object):
    
    _instance = None
    community = Community()
    
    def __init__(self):
        load_dotenv()
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_PORT = os.getenv('DB_PORT')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USERNAME = os.getenv('DB_USERNAME')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.connection_string = f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}"
        self.community = Community()
        
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
        return cls._instance
        
    async def make_query(self, query_text: str, query_params, select_first_row=False):
        conn = await asyncpg.connect(self.connection_string)
        if query_text.startswith('SELECT'):
            if select_first_row:
                results = await conn.fetchrow(query_text, *query_params)
            else:
                results = await conn.fetch(query_text, *query_params)
        else:
            await conn.execute(query_text, *query_params)
            results = None
        
        await conn.close()
        return results
    
    async def get_preys_by_prey_type(self, prey_type: str) -> list:
        query = "SELECT id, name, text, user_id FROM bender_prey WHERE type = $1 AND community_id = $2"
        params = (prey_type, self.community.id)
        rows = await self.make_query(query, params)
        preys_list = []
        if rows is not None:
            for row in rows:
                preys_list.append(Prey(row['id'], row['name'], row['text'], prey_type, row['user_id']))
        return preys_list
    
    async def get_prog_preys(self) -> list:
        return await self.get_preys_by_prey_type('prog')
    
    async def get_my_preys(self) -> list:
        return await self.get_preys_by_prey_type('my')
    
    async def get_com_preys(self) -> list:
        return await self.get_preys_by_prey_type('com')
    
    async def get_prey_by_text_and_type(self, text: str, prey_type: str) -> Union[Prey, None]:
        query = "SELECT id, name, text, user_id FROM bender_prey WHERE type = $1 AND text = $2 AND community_id = $3"    
        params = (prey_type, text, self.community.id)
        prey_row = await self.make_query(query, params, select_first_row=True)
        if prey_row is not None:
            return Prey(prey_row['id'], prey_row['name'], prey_row['text'], prey_type, prey_row['user_id'])
        else:
            return None
    
    async def get_prey_by_id(self, prey_id: int) -> Union[Prey, None]:
        query = "SELECT id, name, text, user_id FROM bender_prey WHERE id = $1"    
        params = (prey_id, self.community.id)
        prey_row = await self.make_query(query, params, select_first_row=True)
        if prey_row is not None:
            return Prey(prey_row['id'], prey_row['name'], prey_row['text'], prey_type, prey_row['user_id'])
        else:
            return None
        
    async def delete_prey(self, prey: Prey) -> list:
        query = "DELETE FROM bender_prey WHERE id = $1"
        params = (prey.prey_id)
        await self.make_query(query, params)
        return await self.get_my_preys()
    
    async def add_prey(self, prey: Prey) -> list:
        query = "INSERT INTO bender_prey (name, text, type, user_id, community_id) VALUES ($1, $2, $3, $4, $5)"
        params = (prey.name, prey.text, prey.prey_type, prey.user_id, self.community.id)
        await self.make_query(query, params)
        return await self.get_my_preys()
    
    async def update_prey_userid(self, prey: Prey, user_id: int) -> Union[Prey, None]:
        query = "UPDATE bender_prey SET user_id = $1 WHERE id = $2"
        params = (user_id, prey.prey_id)
        await self.make_query(query, params)
        return await prey.reread()
        
    async def update_prey_text_and_name(self, prey: Prey, name: str, text: str) -> Union[Prey, None]:
        query = "UPDATE bender_prey SET user_id = $1 WHERE id = $2"
        params = (prey.user_id, prey.prey_id)
        await self.make_query(query, params)
        return await prey.reread()
    
    
    
    
    