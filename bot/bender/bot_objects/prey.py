class Prey(object):
    
    def __init__(self, id: int, name: str, text: str, prey_type: str, user_id: int):
        load_dotenv()
        self.id = id
        self.name = name
        self.text = text
        self.prey_type = prey_type
        self.user_id = user_id
        