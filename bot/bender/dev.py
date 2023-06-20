import os
from dotenv import load_dotenv
import psycopg2    

def get_community():
    load_dotenv()
    return os.getenv('COMMUNITY_ID')

def make_query(query_text, query_params):
    load_dotenv()
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()    
    cursor.execute(query_text, query_params)
    if query_text.startswith('SELECT'):
        results = cursor.fetchall()
    else:
        results = None
    cursor.close()
    if query_text.startswith('SELECT')!=True:
        conn.commit()
        
    conn.close() 
    return results   
