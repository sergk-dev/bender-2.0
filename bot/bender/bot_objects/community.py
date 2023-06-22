from bot_objects.bot import Bot

class Community(object):
    def __init__(self):
        load_dotenv()
        self.COMMUNITY_ID = os.getenv('COMMUNITY_ID')
        self.bot = Bot()
    