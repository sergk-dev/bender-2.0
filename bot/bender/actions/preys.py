# Раздел молитв
import logging
import json
import urllib.parse as urllib

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from bot_utils.db import DB


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

INPUT_TEXT_URL="https://all12steps.ru/botapps/text_input.html?type=pr"
preys_type = ""
prey_id = 0
prey_name = ""
COMMUNITY_ID = get_community()

preys_lists = {"prog": [], "my": [], "com": []}

async def pr_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback_data = str(update.callback_query.data)
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
    keyboard = [
        [InlineKeyboardButton("Программные", callback_data="pr_list_prog")], 
        [
            InlineKeyboardButton("Мои", callback_data="pr_list_my"),
            InlineKeyboardButton("Общие", callback_data="pr_list_com"),
        ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Какие молитвы тебе показать?", reply_markup=reply_markup)

async def pr_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    global preys_type
    
    query = update.callback_query
    if query != None:
        if query.data == 'pr_list_prog':
            preys_type = 'prog'
            user_id = None
        elif query.data == 'pr_list_my':
            preys_type = 'my'
            user_id = query.from_user.id
        else:
            preys_type = 'com'
            user_id = None
    if preys_lists[preys_type] == None or preys_lists[preys_type] == []:
        preys_lists[preys_type] = await fetch_preys(prey_type=preys_type, user_id=user_id)
    keyboard = []
    list_text = ""
    prey_ord = 0
    i=0
    keyboard_row = []
    for prey in preys_lists[preys_type]:
        if i == 5:
            keyboard.append(keyboard_row)
            keyboard_row = []
            i=0
        prey_ord += 1
        i += 1
        keyboard_row.append(InlineKeyboardButton(str(prey_ord), callback_data="pr_show_"+str(prey[0])))
        list_text += str(prey_ord) + ". " + prey[1] + "\n"
    if keyboard_row != []:
        keyboard.append(keyboard_row)
    if list_text == "":
        if preys_type == 'my':
            list_text = "Вы еще не сохранили ни одной молитвы. Возбмите что-то из других списков или добавьте свою."
        else:
            list_text = "Пока никто не добавил молитв в этот список. Возьмите что-то из других списков или добавьте свою."
    if preys_type == 'my':
        keyboard.append([InlineKeyboardButton("Записать свою", web_app=WebAppInfo(url=f"{INPUT_TEXT_URL}&data=&name="))])
    keyboard.append([InlineKeyboardButton("Программные", callback_data="pr_list_prog")])
    keyboard.append([InlineKeyboardButton("Мои", callback_data="pr_list_my"), InlineKeyboardButton("Общие", callback_data="pr_list_com")])
    await query.answer()

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=list_text, reply_markup=reply_markup)
    
async def pr_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    global prey_id
    global preys_lists
    
    query = update.callback_query
    if context.bot_data.get('show_prey_after_delete') != None:
        if context.bot_data['show_prey_after_delete']==True:
            context.bot_data['show_prey_after_delete']=False
        else:
            prey_id = int(str.replace(query.data, 'pr_show_', ''))
    else:
        prey_id = int(str.replace(query.data, 'pr_show_', ''))
        
    user_id = update.callback_query.from_user.id
    if preys_lists[preys_type] == []:
        if preys_type == 'my':
            preys_lists[preys_type] = await fetch_preys(prey_type='my', user_id=user_id)
        else:
            preys_lists[preys_type] = await fetch_preys(prey_type=preys_type, user_id=None)
            
    prey_user_id = 0
    prev_prey_id = 0
    next_prey_id = 0
    prey_text = ""
    prey_name = ""
    for prey_fromlist in preys_lists[preys_type]:
        if prey_fromlist[0] == prey_id:
            index = preys_lists[preys_type].index(prey_fromlist)
            if index > 0:
                prev_prey_id = preys_lists[preys_type][index-1][0]
            if index < len(preys_lists[preys_type])-1: 
                next_prey_id = preys_lists[preys_type][index+1][0]
            prey_name   = prey_fromlist[1]
            prey_text   = prey_fromlist[2]
            prey_user_id = prey_fromlist[3]
            break
    keyboard = []
    keabordRow = []
    if prev_prey_id > 0:
        keabordRow.append(InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"))
    if next_prey_id > 0:
        keabordRow.append(InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")) 
    keyboard.append(keabordRow)           
    if preys_type == 'my':
        text = urllib.quote(prey_text)
        name = urllib.quote(prey_name)
        keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{prey_id}")])
        keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{INPUT_TEXT_URL}&data={text}&name={name}"))])
    elif preys_type == 'com':
        keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")])
        if prey_user_id == query.from_user.id:
            text = urllib.quote(prey_text)
            name = urllib.quote(prey_name)
            keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{INPUT_TEXT_URL}&data={text}&name={name}"))])
    else:
        keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    #await update.effective_message.edit_reply_markup(reply_markup=reply_markup)
    await query.answer()
    await query.edit_message_text(text=prey_text, reply_markup=reply_markup)#InlineKeyboardMarkup([InlineKeyboardButton("...клавиатура загружается...)", callback_data="loading")]))
    
async def pr_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global preys_lists
    global prey_id
    
    user_id = update.callback_query.from_user.id
    if preys_lists[preys_type] == None or preys_lists[preys_type] == []:
        if preys_type == 'my':
            preys_lists[preys_type] = await fetch_preys(prey_type='my', user_id=user_id)
        else:
            preys_lists[preys_type] = await fetch_preys(prey_type=preys_type, user_id=None)
    
    query = update.callback_query
    await delete_prey(prey_id)
    if preys_type=="my":
        user_id=query.from_user.id
        text='Удалил из моих молитв.'
    else:
        user_id= None
        text='Удалил из общих молитв.'
    prev_prey_id = 0
    for prey_fromlist in preys_lists[preys_type]:
        if prey_fromlist[0] == prey_id:
            prey_id = preys_lists[preys_type][preys_lists[preys_type].index(prey_fromlist)-1][0]
            break
    preys_lists[preys_type]= await fetch_preys(prey_type=preys_type, user_id=user_id)
    await query.answer(text)
    context.bot_data['show_prey_after_delete'] = True
    
async def pr_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    global preys_lists
    
    user_id = update.callback_query.from_user.id
    if preys_lists['my'] == None or preys_lists['my'] == []:
        preys_lists['my'] = await fetch_preys(prey_type='my', user_id=user_id)
    if preys_lists[preys_type] == None or preys_lists[preys_type] == []:
        preys_lists[preys_type] = await fetch_preys(prey_type=preys_type, user_id=None)
        
    text = update.effective_message.text
    allready_saved = False
    if preys_lists['my'] != None and len(preys_lists['my']) > 0:
        for prey_fromlist in preys_lists['my']:
            if prey_fromlist[2] == text:
                allready_saved = True
                break
        if allready_saved == False:
            for prey_fromlist in preys_lists[preys_type]:
                if prey_fromlist[0] == prey_id:
                    name = prey_fromlist[1]
                    break
            
        query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES ($1, $2, $3, $4, $5)"
        params = (COMMUNITY_ID, text, 'my', update.callback_query.from_user.id, name)
        await make_query(query, params)
        preys_lists['my'] = await fetch_preys(prey_type='my', user_id=user_id)
        text='Сохранил в мои молитвы.'  
    else:
        text='Уже есть в моих молитвах.'
        
    await update.callback_query.answer(text=text)

async def pr_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Да, уверен", callback_data=f"pr_share_yes_{prey_id}"), InlineKeyboardButton("Нет, не надо", callback_data=f"pr_show_{prey_id}")]]
    await query.edit_message_text(text="Уверен что хочешь выложить молитву в общие?", reply_markup=InlineKeyboardMarkup(keyboard))
        
async def pr_share_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    query = "SELECT id FROM bender_prey WHERE text = $1, type = $2"
    params = (text, 'com')
    results = make_query(query, params)
    if results.count() == 0:
        query = "SELECT name FROM bender_prey WHERE id = $1"
        params = (prey_id)
        results = make_query(query, params)
        query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES ($1, $2, $3, $4, $5)"
        params = (COMMUNITY_ID, text, 'com', update.callback_query.from_user.id, results[0][0])
    else:
        query = "UPDATE bender_prey SET user_id = $1 WHERE id = $2"
        params = (update.callback_query.from_user.id, prey_id)
        make_query(query, params)
    keyboard = [[InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}")]]
    await update.callback_query.answer(text='Сохранил в общие молитвы.', reply_markup=InlineKeyboardMarkup(keyboard))
    
async def pr_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = json.loads(update.effective_message.web_app_data.data)
    if data["type"] == "pr":
        if data["text"] != "":
            if data["old_text"] != "":
                query = "UPDATE bender_prey SET text = $1, name = $2 WHERE id = $3"
                params = (data["text"], data["name"], prey_id)
            else:
                query = "INSERT INTO bender_prey (community_id, text, type, user_id, name) VALUES ($1, $2, $3, $4, $5)"
                params = (COMMUNITY_ID, data["text"], 'my', update.callback_query.from_user.id, data["name"])
            await make_query(query, params)
            
            prev_prey_id = 0
            next_prey_id = 0
            for prey_fromlist in preys_lists[preys_type]:
                if prey_fromlist[0] == prey_id:
                    index = preys_lists[preys_type].index(prey_fromlist)    
                    if index > 0:
                        prev_prey_id = preys_lists[preys_type][index-1][0]
                    if index < len(preys_lists[preys_type])-1: 
                        next_prey_id = preys_lists[preys_type][index+1][0]
                        prey_user_id = prey_fromlist[2]
            
            if preys_type == 'my':
                text = urllib.quote(data["text"])
                name = urllib.quote(data["name"])
                keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{prey_id}")],
                [InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{INPUT_TEXT_URL}&data={text}&name={name}"))]]
            else:
                keyboard = [[InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"), InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")],
                [InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{preys_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{prey_id}")]]
                if prey_user_id == update.callback_query.from_user.id:
                    name = urllib.quote(data["name"])
                    text = urllib.quote(data["text"])
                    keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{INPUT_TEXT_URL}&data={text}&name={name}"))])        
            await update.callback_query.edit_message_text(text=data["text"], reply_markup=InlineKeyboardMarkup(keyboard))