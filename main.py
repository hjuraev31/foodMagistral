import telebot
import sqlite3
from telebot import types
from PIL import Image, ImageDraw, ImageFont

bot = telebot.TeleBot("5777436093:AAFdgVw63Cf9HltwPbZOTc4e_0PfHX8SINs", parse_mode=None)


admin_login = '009'
admin_password = '123'
admins = [531325055]#

class Menu:
    def __init__(self, userid):
        self.count: int = 0
        self.userid: int = userid
        self.meal: str = None
        self.portion: int = None
        self.price: int = None

class Order:
    def __init__(self, userid):
        self.userid:int = userid
        self.meal:str = None
        self.number: str = None
        self.portion: int = None 
        self.image: Image = None
        self.room: str = None

ord_dict = {}

menu_dict = {}


order_dict = {}

count = 0
counter = 0
zakas_soni = 0

#---------------------------------------------------------------------------------

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('meal_db', check_same_thread=False)
    except sqlite3.Error as e:
        print(e)

    return conn

def insert(conn, meal:str, portion:int, price:int):
    cur = conn.cursor()
    cur.execute(f'insert into meal_tbl values ("{meal}", {int(portion)}, {int(price)})')
    conn.commit()
    cur.close()

def clear_table(conn):
    cur = conn.cursor()
    cur.execute('delete from meal_tbl')
    conn.commit()
    cur.close()

def select(conn):
    cur = conn.cursor()
    cur.execute('select * from meal_tbl')
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows

def select_meal_info(conn, meal:str):
    cur = conn.cursor()
    cur.execute(f'select * from meal_tbl where meal = "{meal}"')
    meal_info = cur.fetchone()
    conn.commit()
    cur.close()
    return meal_info

def create_order(conn, userid:int, plus:int = None, portion:int=None,minus: int = None, cancel:int = None, ini:int = None, num: int = None, update: int = None, meal: str = None):
    cur = conn.cursor()
    if plus is not None and plus == 1:
        cur.execute(f'update user_order set portion = portion + 1 where user = "{userid}"')
    elif minus is not None and minus == 1:
        cur.execute(f'update user_order set portion = portion - 1 where user = "{userid}"')
    elif ini is not None and ini == 1:
        # cur.execute(f'select user from user_order')
        # data = cur.fetchall()
        cur.execute(f'update user_order set portion = 0 where user = "{userid}"')

    elif num is not None and num == 1:
        cur.execute(f'select portion from user_order where user = "{userid}"')
        data = cur.fetchone()
        return data
    elif update is not None and update == 1 and meal is not None and portion is not None:
        cur.execute(f'update meal_tbl set portion = portion - {portion} where meal = "{meal}"')
    elif cancel is not None and cancel == 1:
        cur.execute(f'update user_order set portion = 0 where user = "{userid}"')

def add_user_to_ord(conn, userid):
    cur = conn.cursor()
    cur.execute(f'select user from user_order where user = "{userid}"')
    user = cur.fetchone()
    if user is None:
        cur.execute(f'insert into user_order values (0, "{userid}", null)')
    elif user is not None:
        pass

def generate_check(message, text, ord_data):

    ord_data.image = Image.new('RGB', (400,250), color = (255, 255, 255)) 

    d = ImageDraw.Draw(ord_data.image)
    font = ImageFont.truetype('times.ttf', 22)
    d.text((10,10), text, fill=(0,0,0), font=font)
    bot.send_photo(message.chat.id, ord_data.image)

conn = create_connection()




def show_menu(message):
            markup = types.InlineKeyboardMarkup()
            markup.row_width = 2
            i = 0
            while i < len(select(conn))-1: 
                global counter
                counter += 1
                btn = types.InlineKeyboardButton(select(conn)[i][0], callback_data=f'order{select(conn)[i][0]}')
                i+=1
                counter +=1
                sec_btn = types.InlineKeyboardButton(select(conn)[i][0], callback_data=f'order{select(conn)[i][0]}')
                i+=1
                markup.add(btn,sec_btn)
                if len(select(conn)) % 2 != 0 and len(select(conn))-1 == i:
                    markup.add(types.InlineKeyboardButton(select(conn)[i][0], callback_data=f'order{select(conn)[i][0]}'))
            close_btn = types.InlineKeyboardButton('Yopish❌', callback_data='close_menu')
            markup.add(close_btn)
            bot.send_message(message.chat.id,"Bugungi menyu", reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    userid = message.chat.id
    photo = open("meal.jpeg","rb")
    bot.send_photo(userid,photo)
    #-------------------
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard = True)
    btn1 = types.KeyboardButton("Murojat✏️")
    btn2 = types.KeyboardButton("Bot haqida♻️")
    btn3 = types.KeyboardButton("Bugungi menyu📃")
    markup.add(btn1,btn2)
    markup.add(btn3)
    bot.send_message(userid,"Assalomu aleykum "+message.from_user.first_name+" O'qituvchilar uchun Magistral Food dastavka botiga xush kelibsiz".format(message.from_user), reply_markup=markup)



@bot.message_handler(content_types=["text"])
def murojat(message):
    if message.text =="Murojat✏️":
        bot.send_message(message.chat.id,"Adminga murojatingiz bo'lsa yoki qandaydir shikoyatingiz bo'lsa @Luqmonjon_M_0908 ga yozib jo'nating sizni fikringiz biz uchun muhim!")
        bot.register_next_step_handler(message,get_yozgani)
        def get_yozgani():
         text_user = message.text
         bot.send_message(chat_id="-1001673651278",text = text_user)   
         print(text_user)   
    elif message.text =="Bot haqida♻️":
        bot.send_message(message.chat.id,"Assalomu aleykum bot orqali turli xildagi taomlarni buyurtma qilishingiz mumkin \nBuyurtma berish uchun  BUGUNGI MENYU tugmasini bosing")
    elif message.text =="Bugungi menyu📃":
        add_user_to_ord(conn, message.from_user.id)
        show_menu(message)

    elif message.text == '/admin':
        verify(message)
    else:
        bot.send_message(message.chat.id,"uzur sizni chunmadim ")



@bot.message_handler(commands=['admin'])
def verify(message):
    if message.chat.id in admins:
        successful_login(message)
    else:
        bot.send_message(message.chat.id, 'Admin loginini kiriting!')
        bot.register_next_step_handler(message, check_login)

def successful_login(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    menu_add_btn = types.InlineKeyboardButton("Taom qoshish➕",  callback_data="change")
    delete_previous_menu = types.InlineKeyboardButton("Menyuni ochirish🗑", callback_data='delete_menu')
    menu_btn = types.InlineKeyboardButton('Menyu📃',callback_data='open_menu')
    keyboard.add(menu_add_btn, delete_previous_menu)
    keyboard.add(menu_btn)
    bot.send_message(message.chat.id, 'Siz tizimga kirdingiz', reply_markup=keyboard)

def check_login(message):
    login = message.text
    if login == admin_login:
        bot.send_message(message.chat.id, 'Parolingizni kiriting!')
        bot.register_next_step_handler(message, checkpwd)
    else:
        bot.send_message(message.chat.id, 'Login xato qaytatdan urinib koring!')        
        bot.register_next_step_handler(message,check_login)

def checkpwd(message):
    pwd = message.text
    if admin_password == pwd:
        successful_login(message)
        admins.append(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Parol xato qaytatdan urinib koring!')        
        bot.register_next_step_handler(message,checkpwd)


@bot.callback_query_handler(func=lambda call: True)
def update_menu(call):
    order = str(call.data[0:5])
    meal_to_get_info = str(call.data[5:])
    global zakas_soni
    msgid = call.message.message_id
    match call.data:
        case 'change':
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Taom kiriting')
            bot.register_next_step_handler(call.message, get_meal)
            
        case 'delete_menu':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 2
            do_del = types.InlineKeyboardButton("Ha🟢",  callback_data="do_delete")
            do_not = types.InlineKeyboardButton("Yo`q🔴", callback_data='dont_delete')
            keyboard.add(do_del, do_not)
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Menyuni ochirib yangi qoshmoqcimisiz?', reply_markup=keyboard)
        case 'save':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 2
            menu_add_btn = types.InlineKeyboardButton("Taom qoshish➕",  callback_data="change")
            delete_previous_menu = types.InlineKeyboardButton("Menyuni ochirish🗑", callback_data='delete_menu')
            menu_btn = types.InlineKeyboardButton('Menyu📃',callback_data='open_menu')
            keyboard.add(menu_add_btn, delete_previous_menu)
            keyboard.add(menu_btn)
            bot.edit_message_text("Taomlar kiritildi", chat_id=call.from_user.id, message_id=call.message.message_id,reply_markup=keyboard)
            
        case 'dont_delete':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 2
            menu_add_btn = types.InlineKeyboardButton("Taom qoshish➕",  callback_data="change")
            delete_previous_menu = types.InlineKeyboardButton("Menyuni ochirish🗑", callback_data='delete_menu')
            keyboard.add(menu_add_btn, delete_previous_menu)
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Admin menu', reply_markup=keyboard)
        case 'do_delete':
            clear_table(conn)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 2
            menu_add_btn = types.InlineKeyboardButton("Taom qoshish➕",  callback_data="change")
            delete_previous_menu = types.InlineKeyboardButton("Menyuni ochirish🗑", callback_data='delete_menu')
            keyboard.add(menu_add_btn, delete_previous_menu)
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Menu ochirildi', reply_markup=keyboard)
        case 'open_menu':
            show_menu(call.message)
        case 'close_menu':
            bot.delete_message(call.from_user.id, call.message.message_id)    
        case 'plus_ord':
            create_order(conn, userid=call.from_user.id, plus=1)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 3
            zakas_soni += 1
            qoshish =  types.InlineKeyboardButton("➕",  callback_data='plus_ord')
            ayirish =  types.InlineKeyboardButton("➖",  callback_data='minus_ord')
            ortasi =  types.InlineKeyboardButton(f"{create_order(conn, userid=call.from_user.id, num=1)[0]}", callback_data='noneUsedCounter')
            zakaz = types.InlineKeyboardButton('Buyurtma berish✅', callback_data='zakaz')
            otmen = types.InlineKeyboardButton('Bekor qilish', callback_data='otmen')
            keyboard.add(ayirish,ortasi,qoshish)
            keyboard.add(zakaz, otmen)
            bot.edit_message_reply_markup(call.from_user.id, message_id=msgid, reply_markup=keyboard)
            

        case 'minus_ord':
            if create_order(conn, userid=call.from_user.id, num=1)[0] == 0 :
                pass
            else :
                create_order(conn, minus=1, userid=call.from_user.id)
                keyboard = types.InlineKeyboardMarkup()
                keyboard.row_width = 3
                qoshish =  types.InlineKeyboardButton("➕",  callback_data='plus_ord')
                ayirish =  types.InlineKeyboardButton("➖",  callback_data='minus_ord')
                ortasi =  types.InlineKeyboardButton(f"{create_order(conn, num = 1, userid=call.from_user.id)[0]}", callback_data='noneUsedCounter')
                zakaz = types.InlineKeyboardButton('Buyurtma berish✅', callback_data='zakaz')
                otmen = types.InlineKeyboardButton('Bekor qilish', callback_data='otmen')
                keyboard.add(ayirish,ortasi,qoshish)
                keyboard.add(zakaz, otmen)
                bot.edit_message_reply_markup(call.from_user.id, message_id=msgid, reply_markup=keyboard)    
        
        case 'zakaz':
            ord_data = Order(call.from_user.id)
            ord_dict[call.from_user.id] = ord_data
            ord_data.meal = call.message.text[16:call.message.text.find('\n')]
            ord_data.portion = create_order(conn, num = 1, userid=call.from_user.id)[0]
            create_order(conn,userid=call.from_user.id, update=1, meal=ord_data.meal, portion=create_order(conn, num = 1, userid=call.from_user.id)[0])
            create_order(conn, ini=1, userid=call.from_user.id)
            bot.delete_message(call.from_user.id, msgid)
            bot.send_message(call.from_user.id, 'Telefon raqamingizni kiriting \nMaslan +998901234567')
            bot.register_next_step_handler(call.message, callback=get_phone_number, ord_data=ord_data)

        case 'otmen':
            bot.delete_message(call.from_user.id, msgid)
            create_order(conn, userid=call.from_user.id, cancel=1)

        case order:
            create_order(conn, ini=1, userid=call.from_user.id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row_width = 3
            qoshish =  types.InlineKeyboardButton("➕",  callback_data='plus_ord')
            ayirish =  types.InlineKeyboardButton("➖",  callback_data='minus_ord')
            ortasi =  types.InlineKeyboardButton(f"{create_order(conn, userid=call.from_user.id, num =1)[0]}", callback_data='noneUsedCounter')
            zakaz = types.InlineKeyboardButton('Buyurtma berish✅', callback_data='zakaz')
            otmen = types.InlineKeyboardButton('Bekor qilish', callback_data='otmen')
            keyboard.add(ayirish,ortasi,qoshish)
            keyboard.add(zakaz, otmen)
            bot.send_message(call.from_user.id, f'Tanlangan taom: {select_meal_info(conn, meal_to_get_info)[0]}\nPortsiya narxi: {select_meal_info(conn, meal_to_get_info)[2]}\nNechta portsiya qolgan: {select_meal_info(conn, meal_to_get_info)[1]}',reply_markup=keyboard)
            msgid = call.message.message_id



def get_phone_number(message, ord_data):
    ord_data.number = message.text
    bot.send_message(message.chat.id, 'Xonangizni raqamini kiriting')
    # generate_check(message, f'Taom: "{ord_data.meal}"\nPortsiyalar soni: {ord_data.portion}\nNarxi:{select_meal_info(conn, ord_data.meal)[2] * ord_data.portion}\nBuyurtmachi raqami: {ord_data.number}\nXona raqami:', ord_data=ord_data)
    bot.register_next_step_handler(message, callback=get_room_number, ord_data=ord_data)

def get_room_number(message, ord_data):
    ord_data.room = message.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width=3
    menu = types.InlineKeyboardButton('Menyu📃', callback_data='open_menu')
    keyboard.add(menu)
    generate_check(message, f'Taom: {ord_data.meal}\nPortsiyalar soni: {ord_data.portion}\nNarxi: {select_meal_info(conn, ord_data.meal)[2]}\nBuyurtmachi raqami: {ord_data.number}\nXona raqami: {ord_data.room}\nBuyurtmachi ismi:\n{message.from_user.first_name}\n\nJami bo`lib: {select_meal_info(conn, ord_data.meal)[2] * ord_data.portion}', ord_data=ord_data)
    bot.send_message(message.chat.id, 'Sizning chekingiz', reply_markup=keyboard)
    bot.send_photo(chat_id="-1001673651278",photo = ord_data.image)  
    bot.send_message("-1001673651278", f'Buyurtmachi telegrami: @{message.from_user.username}')
def get_meal(message):
    global count
    data = Menu(message.chat.id)
    count += 1
    menu_dict[count] = data
    data = menu_dict[count]
    meal = message.text
    data.meal = meal
    bot.delete_message(message.chat.id, message.message_id)
    bot.edit_message_text("Nechta portsiya bor?", chat_id=message.chat.id, message_id=message.message_id-1)
    bot.register_next_step_handler(message, get_portion)

def get_portion(message):
    global count
    try: 
        portion = int(message.text)
        data = menu_dict[count]
        data.portion = portion
        bot.delete_message(message.chat.id,message.message_id)
        bot.edit_message_text("Portsiyasi necpul?", chat_id=message.chat.id, message_id=message.message_id-2)
        bot.register_next_step_handler(message, get_price)
    except ValueError:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row_width = 1
        menu_add_btn = types.InlineKeyboardButton("Togirlash✏️",  callback_data="change")
        keyboard.add(menu_add_btn)
        bot.send_message(message.chat.id, 'Portsiyalar, son sifatida kiritilishi kerak!', reply_markup=keyboard)

def get_price(message):
    global count
    price = message.text
    data = menu_dict[count]
    data.price = price
    data.count += 1
    print(data.count)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row_width = 2
    menu_add_btn = types.InlineKeyboardButton("➕",  callback_data="change")
    save_menu = types.InlineKeyboardButton("✔️", callback_data='save')
    keyboard.add(menu_add_btn, save_menu)
    insert(conn, data.meal, data.portion, data.price)
    bot.delete_message(message.chat.id, message.message_id)
    bot.edit_message_text("Yana qoshish uchun ➕ bosin saqlash uchun ✔️", chat_id=message.chat.id, message_id=message.message_id-3,reply_markup=keyboard)
    


    

bot.infinity_polling()
