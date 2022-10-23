# import sqlite3


# def create_connection():
#     conn = None
#     try:
#         conn = sqlite3.connect('meal_db', check_same_thread=False)
#     except sqlite3.Error as e:
#         print(e)

#     return conn

# conn = create_connection()

# cur = conn.cursor()
# cur.execute(f'select user from user_order')
# # cur.execute(f'select portion from user_order where user = "{531325055}"')
# data = cur.fetchone()
# print(data == None)


from PIL import Image, ImageDraw
 
img = Image.new('RGB', (180,300), color = (255, 255, 255))
 
d = ImageDraw.Draw(img)
text = 'Taom: osh\nPortsiya: 4\nNarxi: 120000'
d.text((10,10), text, fill=(0,0,0))
 
img.save('pil_text.png')