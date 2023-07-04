from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes
import urllib.parse as urllib

from bot_objects.bot import Bot
from bot_objects.community import Community
from bot_objects.prey import Prey
from bot_utils.db import DB

class Act_preys(object):
        
    def __init__(self):
        self.preys_type = ''
        self.bot = Bot()
        self.community = Community()
        self.db = DB()
        self.user_id = None
        self.preys_lists = {"prog": [], "my": [], "com": []}
        self.INPUT_TEXT_URL="https://all12steps.ru/botapps/text_input.html?type=pr"
        self.prey = None
        
    async def pr_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
         
        if update.callback_query is None:
            return
        
        callback_data = str(update.callback_query.data)
        if callback_data.startswith('pr_list'):
            await self.pr_list(update, context)
        elif callback_data.startswith('pr_show'):
            await self.pr_show(update, context)
        elif callback_data.startswith('pr_delete'):
            await self.pr_delete(update, context)
        elif callback_data.startswith('pr_save'):
            await self.pr_save(update, context)
        elif callback_data.startswith('pr_share'):
            if callback_data.startswith('pr_share_yes'):
                await self.pr_share_yes(update, context)
            else:
                await self.pr_share(update, context)
                
    async def pr_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [InlineKeyboardButton("Программные", callback_data="pr_list_prog")], 
            [
                InlineKeyboardButton("Мои", callback_data="pr_list_my"),
                InlineKeyboardButton("Общие", callback_data="pr_list_com"),
            ],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message is not None:
            await update.message.reply_text("Какие молитвы тебе показать?", reply_markup=reply_markup)
        
    async def pr_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
        query = update.callback_query
        if query is None:
            return
        
        if query.data == 'pr_list_prog':
            self.preys_type = 'prog'
            self.user_id = 0
            if self.preys_lists[self.preys_type] == []:
                self.preys_lists[self.preys_type] = await self.db.get_prog_preys()
        elif query.data == 'pr_list_my':
            self.preys_type = 'my'
            self.user_id = query.from_user.id
            if self.preys_lists[self.preys_type] == []:
                self.preys_lists[self.preys_type] = await self.db.get_my_preys(user_id=self.user_id)
        else:
            self.preys_type = 'com'
            self.user_id = 0
            self.preys_lists[self.preys_type] = await self.db.get_com_preys()
        
        keyboard = []
        list_text = ""
        prey_ord = 0
        i=0
        keyboard_row = []
        for prey in self.preys_lists[self.preys_type]:
            if i == 5:
                keyboard.append(keyboard_row)
                keyboard_row = []
                i=0
            prey_ord += 1
            i += 1
            keyboard_row.append(InlineKeyboardButton(str(prey_ord), callback_data="pr_show_"+str(prey.prey_id)))
            list_text += str(prey_ord) + ". " + prey.name + "\n"
        if keyboard_row != []:
            keyboard.append(keyboard_row)
        if list_text == "":
            if self.preys_type == 'my':
                list_text = "Вы еще не сохранили ни одной молитвы. Возбмите что-то из других списков или добавьте свою."
            else:
                list_text = "Пока никто не добавил молитв в этот список. Возьмите что-то из других списков или добавьте свою."
        if self.preys_type == 'my':
            keyboard.append([InlineKeyboardButton("Записать свою", web_app=WebAppInfo(url=f"{self.INPUT_TEXT_URL}&data=&name="))])
        keyboard.append([InlineKeyboardButton("Программные", callback_data="pr_list_prog")])
        keyboard.append([InlineKeyboardButton("Мои", callback_data="pr_list_my"), InlineKeyboardButton("Общие", callback_data="pr_list_com")])
        await query.answer()

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=list_text, reply_markup=reply_markup)
        
    async def pr_show(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
        query = update.callback_query
        if query is None:
            return
        
        prey_id = 0
        if context.chat_data is None:
            context.chat_data = {}
        if context.chat_data.get('show_prey_after_delete') != None & context.chat_data['pray_id'] != None:
            if context.chat_data['show_prey_after_delete']==True:
                context.chat_data['show_prey_after_delete']=False
                prey_id = context.chat_data['pray_id']
            else:
                prey_id = int(str.replace(str(query.data), 'pr_show_', ''))
        else:
            prey_id = int(str.replace(str(query.data), 'pr_show_', ''))
        
        self.user_id = query.from_user.id
        
        if self.preys_type == 'my':
            if self.preys_lists[self.preys_type] == []:
                self.preys_lists[self.preys_type] = await self.db.get_my_preys(user_id=query.from_user.id)
        elif self.preys_type == 'com':
            self.preys_lists[self.preys_type] = await self.db.get_com_preys()
        
        prev_prey_id = 0
        next_prey_id = 0    
        for prey_fromlist in self.preys_lists[self.preys_type]:
            if prey_fromlist.prey_id == prey_id:
                index = self.preys_lists[self.preys_type].index(prey_fromlist)
                if index > 0:
                    prev_prey_id = self.preys_lists[self.preys_type][index-1].prey_id
                if index < len(self.preys_lists[self.preys_type])-1: 
                    next_prey_id = self.preys_lists[self.preys_type][index+1][0]
            self.pray = prey_fromlist
            break
        keyboard = []
        keabordRow = []
        if prev_prey_id > 0:
            keabordRow.append(InlineKeyboardButton("<- предыдущая", callback_data=f"pr_show_{prev_prey_id}"))
        if next_prey_id > 0:
            keabordRow.append(InlineKeyboardButton("следующая ->", callback_data=f"pr_show_{next_prey_id}")) 
        keyboard.append(keabordRow)           
        if self.pray.prey_type == 'my':
            text = urllib.quote(self.pray.text)
            name = urllib.quote(self.pray.name)
            keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{self.pray.prey_type}"), InlineKeyboardButton("Поделиться со всеми", callback_data=f"pr_share_{self.pray.prey_id}")])
            keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{self.pray.prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{self.INPUT_TEXT_URL}&data={text}&name={name}"))])
        elif self.pray.prey_type == 'com':
            keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{self.pray.prey_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{self.pray.prey_id}")])
            if self.pray.user_id == query.from_user.id:
                text = urllib.quote(self.pray.text)
                name = urllib.quote(self.pray.name)
                keyboard.append([InlineKeyboardButton("Удалить", callback_data=f"pr_delete_{self.pray.prey_id}"), InlineKeyboardButton("Изменить", web_app=WebAppInfo(url=f"{self.INPUT_TEXT_URL}&data={text}&name={name}"))])
        else:
            keyboard.append([InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{self.pray.prey_type}"), InlineKeyboardButton("Сохранить в мои", callback_data=f"pr_save_{self.pray.prey_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        await query.answer()
        await query.edit_message_text(text=self.pray.text, reply_markup=reply_markup)
        
    async def pr_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        query = update.callback_query
        if query is None:
            return
        
        await self.db.delete_prey(self.pray)
        if self.preys_type=="my":
            self.user_id=query.from_user.id
            text='Удалил из моих молитв.'
        else:
            self.user_id= None
            text='Удалил из общих молитв.'
        
        await query.answer(text)
        
        if self.preys_type == 'my':
            self.preys_lists[self.preys_type] = await self.db.get_my_preys(user_id=query.from_user.id)
        else:
            self.preys_lists[self.preys_type] = await self.db.get_com_preys()
        
        prev_prey = None
        if len(self.preys_lists[self.preys_type])=0:
            prev_prey = None
        elif len(self.preys_lists[self.preys_type])=1:
            prev_prey = self.preys_lists[self.preys_type][0]
        else:    
            for prey_fromlist in self.preys_lists[self.preys_type]:
                if prey_fromlist == self.pray:
                    current_index = self.preys_lists[self.preys_type].index(prey_fromlist)
                    if current_index > 0:
                        prev_prey = self.preys_lists[self.preys_type][current_index-1]
                    break
        
        if prev_prey is None:
            await self.pr_list(update, context)
        else:
            if context.chat_data is None:
                context.chat_data = {}
            context.chat_data['show_prey_after_delete'] = True
            context.chat_data['pray_id'] = prev_prey.prey_id
            await self.pr_show(update, context)
        
    async def pr_share(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None:
            return
        await query.answer()
        keyboard = [[InlineKeyboardButton("Да, уверен", callback_data=f"pr_share_yes"), InlineKeyboardButton("Нет, не надо", callback_data=f"pr_show_{self.pray.prey_id}")]]
        await query.edit_message_text(text="Уверен что хочешь выложить молитву в общие?", reply_markup=InlineKeyboardMarkup(keyboard))
            
    async def pr_share_yes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None:
            return
        text = self.pray.text
        prey = await self.db.get_prey_by_text_and_type(text, 'com')
        if prey is None:
            await self.db.add_prey(self.pray, 'com')
        else:
            await self.db.update_prey_userid(prey, query.from_user.id)
        keyboard = [[InlineKeyboardButton("Назад к списку", callback_data=f"pr_list_{self.preys_type}")]]
        await query.answer()
        await query.edit_message_text(text='Сохранил в общие молитвы.', reply_markup=InlineKeyboardMarkup(keyboard))
        
    async def pr_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if query is None:
            return
        
        text = self.pray.text
        allready_saved = False
        if len(self.preys_lists['my']) > 0:
            for prey_fromlist in self.preys_lists['my']:
                if prey_fromlist.text == text:
                    allready_saved = True
                    break
        if allready_saved == False:        
            await self.db.add_prey(self.pray, 'my')
            self.preys_lists['my'] = await self.db.get_my_preys(user_id=query.from_user.id)
            text='Сохранил в мои молитвы.'  
        else:
            text='Уже есть в моих молитвах.'
        
        await query.answer(text=text)