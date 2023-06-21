import os
from dotenv import load_dotenv
import asyncpg    

def get_community():
    load_dotenv()
    return int(os.getenv('COMMUNITY_ID'))

async def make_query(query_text, query_params):
    load_dotenv()
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    conn = await asyncpg.connect(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    if query_text.startswith('SELECT'):
        results = await conn.fetch(query_text, *query_params)
    else:
        results = None
        await conn.execute(query_text, *query_params)
        
    await conn.close()
     
    return results   
