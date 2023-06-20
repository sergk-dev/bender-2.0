import logging

import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes
from .dev import make_query, get_community
import urllib.parse as urllib

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

preys_list = []
preys_type = ""
prey_id = 0
prey_name = ""
community_id = get_community()

async def pr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
    if callback_data.startswith('pr_list'):
        await pr_list(update, context)
    elif callback_data.startswith('pr_show'):
        await pr_show(update, context)
    elif callback_data.startswith('pr_delete'):
        await pr_delete(update, context)
    elif callback_data.startswith('pr_save'):
        await pr_save(update, context)
    elif callback_data.startswith('pr_share'):
        if callback_data.startswith('pr_share_yes'):
            await pr_share_yes(update, context)
        else:
            await pr_share(update, context)        
    
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

def fetch_preys(prey_type, user_id=None):
    
    if user_id:
        query = "SELECT id, name FROM bender_prey WHERE type = %s AND user_id = %s"
        params = (prey_type, user_id)
    else:
        query = "SELECT id, name FROM bender_prey WHERE type = %s"
        params = (prey_type,)
        
    results = make_query(query, params)
    
    preys_list = results
    
    return results

def delete_prey(prey_id) -> None:
    
    query = "DELETE FROM bender_prey WHERE id = %s"
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
    i = 0
    for prey in preys:
        i=0
        keyboard_row = []
        while i<=5:
            keyboard_row.append(InlineKeyboardButton(prey[1], callback_data="pr_show_"+str(prey[0])))
        keyboard.append(keyboard_row)
        i += 1
        list += f" + {i}. {prey["name"]} + "\n"
    if preys_type == 'my':
        keyboard.append([InlineKeyboardButton("Записать свою", web_app=WebAppInfo(url=f"https://all12steps.ru/botapps/text_input.html?data=&type=pr&name="))])
    keyboard.append([InlineKeyboardButton("Программные", callback_data="pr_list_prog")])
    keyboard.append([InlineKeyboardButton("Мои", callback_data="pr_list_my"), InlineKeyboardButton("Общие", callback_data="pr_list_com")])
    await query.answer()

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=list, reply_markup=reply_markup)
    
async def pr_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    prey_id = int(str.replace(query.data, 'pr_show_', ''))
    prey_user_id = 0
    for prey_fromlist in preys_list:
        if prey_fromlist[0] == prey_id:
            prev_prey_id = preys_list[prey_fromlist.index-1][0]
            next_prey_id = preys_list[prey_fromlist.index+1][0]
            prey_user_id = prey_fromlist[2]
            break
        
    if preys_type == 'my':
        text = urllib.quote(update.effective_message.text)
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{prey_id}")]
                [InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"https://all12steps.ru/botapps/text_input.html?data={text}&type=pr"))]]
    elif preys_type == 'com':
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
        if prey_user_id = query.from_user.id
            text = urllib.quote(update.effective_message.text)
            keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"https://all12steps.ru/botapps/text_input.html?data={text}&type=pr"))])
    else:
        keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
    
    await query.answer()

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=preys[0][1], reply_markup=reply_markup)
    
async def pr_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    delete_prey(prey_id)
    await query.answer(text='Удалил из моих молитв.')
    
async def pr_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    query = "SELECT id FROM bender_prey WHERE text = %s, type = %s"
    params = (text, 'my')
    results = make_query(query, params)
    if results.count() == 0:
        query = "SELECT name FROM bender_prey WHERE id = %s"
        params = (prey_id)
        results = make_query(query, params)
        
        query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES (%s, %s, %s, %s, %s)"
        params = (community_id, text, 'my', update.callback_query.from_user.id, results[0][0])
        make_query(query, params)

    await update.callback_query.answer(text='Сохранил в мои молитвы.')

async def pr_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Да, уверен", callback_data=f"pr_share_yes_{prey_id}"), InlineKeyboardButton("Нет, не надо", callback_data=f"pr_show_{prey_id}")]]
    await query.edit_message_text(text="Уверен что хочешь выложить молитву в общие?", reply_markup=InlineKeyboardMarkup(keyboard))
        
async def pr_share_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    query = "SELECT id FROM bender_prey WHERE text = %s, type = %s"
    params = (text, 'com')
    results = make_query(query, params)
    if results.count() == 0:
        query = "SELECT name FROM bender_prey WHERE id = %s"
        params = (prey_id)
        results = make_query(query, params)
        query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES (%s, %s, %s, %s, %s)"
        params = (community_id, text, 'com', update.callback_query.from_user.id, results[0][0])
    else:
        query = "UPDATE bender_prey SET user_id = %s WHERE id = %s"
        params = (update.callback_query.from_user.id, prey_id)
        make_query(query, params)
    keyboard = [[InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}")]]
    await update.callback_query.answer(text='Сохранил в общие молитвы.', reply_markup=InlineKeyboardMarkup(keyboard))
    
async def pr_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = json.loads(update.effective_message.web_app_data.data)
    if data["type"] == "pr":
        if data["text"] != "":
            if data["old_text"] != "":
                query = "UPDATE bender_prey SET text = %s, name = %s WHERE id = %s"
                params = (data["text"], data["name"], prey_id)
            else:
                query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES (%s, %s, %s, %s, %s)"
                params = (community_id, data["text"], 'my', update.callback_query.from_user.id, data["name"])
            make_query(query, params)
            for prey_fromlist in preys_list:
                if prey_fromlist[0] == prey_id:
                    prev_prey_id = preys_list[prey_fromlist.index-1][0]
                    next_prey_id = preys_list[prey_fromlist.index+1][0]
                    prey_user_id = prey_fromlist[2]
                    break
            if preys_type == 'my':
                text = urllib.quote(update.effective_message.text)
                keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{prey_id}")]
                [InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"https://all12steps.ru/botapps/text_input.html?data={text}&type=pr"))]]
            else:
                keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
                if prey_user_id = query.from_user.id
                    text = urllib.quote(update.effective_message.text)
                    keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"https://all12steps.ru/botapps/text_input.html?data={text}&type=pr"))])        
            await query.edit_message_text(text=data["text"], reply_markup=InlineKeyboardMarkup(keyboard))