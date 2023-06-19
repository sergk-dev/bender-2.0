import logging
import psycopg2

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

preys_list = []
preys_type = None

async def pr_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("Программные", callback_data="pr_list_prog")], 
        [
            InlineKeyboardButton("Мои", callback_data="pr_list_my"),
            InlineKeyboardButton("Общие", callback_data="pr_list_com"),
        ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Какие молитвы тебе показать?", reply_markup=reply_markup)

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
    conn.close() 
    return results   

def fetch_preys(prey_type, user_id=None):
    
    if user_id:
        query = "SELECT id, name FROM preys WHERE type = %s AND user_id = %s"
        params = (prey_type, user_id)
    else:
        query = "SELECT id, name FROM preys WHERE type = %s"
        params = (prey_type,)
        
    results = make_query(query, params)
    
    preys_list = results
    
    return results

def fetch_prey(prey_id):
    
    query = "SELECT id, text, user_id FROM preys WHERE id = %s"
    params = (prey_id)
        
    results = make_query(query, params)
     
    return results

def delete_prey(prey_id) -> None:
    
    query = "DELETE FROM preys WHERE id = %s"
    params = (prey_id)
        
    make_query(query, params)

async def pr_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data = 'pr_list_prog':
        type = 'prog'
        user_id = None
    elif query.data = 'pr_list_my':
        type = 'my'
        user_id = query.from_user.id
    else:
        type = 'com'
        user_id = None
    preys_type = type    
    preys = fetch_preys(prey_type=type, user_id=user_id)
    keyboard = []
    list = ""
    for prey in preys:
        i=0
        keyboard_row = []
        while i<=5:
            keyboard_row.append(InlineKeyboardButton(prey[1], callback_data="pr_show_"+str(prey[0])))
        keyboard.append(keyboard_row)
        list += prey.name + "\n"
    keyboard.append([InlineKeyboardButton("Программные", callback_data="pr_list_prog"), InlineKeyboardButton("Мои", callback_data="pr_list_my"), InlineKeyboardButton("Общие", callback_data="pr_list_com")])
    await query.answer()

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=list, reply_markup=reply_markup)
    
async def pr_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(replace(query.data, 'pr_show_', ''))
    preys = fetch_prey(prey_id)
    prey_user_id = 0
    for prey_fromlist in preys_list:
        if prey_fromlist[0] == prey_id:
            prev_prey_id = preys_list[prey_fromlist.index-1][0]
            next_prey_id = preys_list[prey_fromlist.index+1][0]
            prey_user_id = prey_fromlist[2]
            break
        
    if preys_type == 'my':
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{prey_id}")]
                [InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", callback_data=f"pr_change_{prey_id}")]]
    elif preys_type == 'com':
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
        if prey_user_id = query.from_user.id
            keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}")])
    else:
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
    
    await query.answer()

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=preys[0][1], reply_markup=reply_markup)
    
async def pr_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(replace(query.data, 'pr_delete_', ''))
    delete_prey(prey_id)
    await query.answer(text='Удалил из моих молитв.')
    
async def pr_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(replace(query.data, 'pr_save_', ''))
    query = "SELECT text FROM preys WHERE id = %s"
    params = (prey_id)
    results = make_query(query, params)
    text = results[0][0]
    query = "SELECT id FROM preys WHERE text = %s, type = %s"
    params = (text, 'my')
    results = make_query(query, params)
    if results.count() == 0:
        query = "INSERT INTO preys (text, type, user_id) VALUES (%s, %s, %s)"
        params = (text, 'my', query.from_user.id)
        make_query(query, params)

    await query.answer(text='Сохранил в мои молитвы.')

async def pr_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(replace(query.data, 'pr_share_', ''))
    await query.answer()
    keyboard = [[InlineKeyboardButton("Да, уверен", callback_data=f"pr_share_yes_{prey_id}"), InlineKeyboardButton("Нет, не надо", callback_data=f"pr_show_{prey_id}")]]
    await query.edit_message_text(text="Уверен что хочешь выложить молитву в общие?", reply_markup=InlineKeyboardMarkup(keyboard))
        
async def pr_share_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(replace(query.data, 'pr_share_yes_', ''))
    query = "SELECT text FROM preys WHERE id = %s"
    params = (prey_id)
    results = make_query(query, params)
    text = results[0][0]
    query = "SELECT id FROM preys WHERE text = %s, type = %s"
    params = (text, 'com')
    results = make_query(query, params)
    if results.count() == 0:
        query = "INSERT INTO preys (text, type, user_id) VALUES (%s, %s, %s)"
        params = (text, 'com', query.from_user.id)
    else:
        query = "UPDATE preys SET user_id = %s WHERE id = %s"
        params = (query.from_user.id, prey_id)
        make_query(query, params)
    keyboard = [[InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}")]]
    await query.answer(text='Сохранил в общие молитвы.', reply_markup=InlineKeyboardMarkup(keyboard))
    

    