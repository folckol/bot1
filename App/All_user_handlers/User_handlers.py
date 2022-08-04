import asyncio
import sqlite3

from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext

from Kwork_order_bot.App.Classes.States_classes import Start_waiting_group
from Kwork_order_bot.App.All_user_handlers.Main_menu_handlers import Main_menu

database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\database.db')
sql = database.cursor()

admin_database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\admin_database.db')
admin_sql = admin_database.cursor()

async def mailing_choice(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Нет']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Да':

        mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        mailing_keyboard.add('Ввести промокод')
        mailing_keyboard.add('Подписаться')

        await message.answer('Хотите ввести промокод для эксклюзивной подписки?', reply_markup=mailing_keyboard)

        await Start_waiting_group.mailing_choice_2.set()

    elif message.text == 'Нет':

        sql.execute(f"UPDATE user_database SET mailing = 'off' WHERE id = ({message.from_user.id})")
        database.commit()

        sql.execute(f"SELECT * FROM user_database WHERE id = ({message.from_user.id})")
        print(sql.fetchall())

        await message.answer('Вы успешно подписались на рассылку!')
        await asyncio.sleep(1)
        await Main_menu(message, state)


async def mailing_choice_next(message: Message, state: FSMContext):

    if message.text not in ['Ввести промокод', 'Подписаться']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Ввести промокод':
        promo_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        promo_keyboard.add('Отмена')

        await message.answer('Введите промокод', reply_markup=promo_keyboard)
        await Start_waiting_group.waiting_promo.set()

    if message.text == 'Подписаться':
        sql.execute(f"UPDATE user_database SET mailing = 'default' WHERE id = {message.from_user.id}")
        database.commit()

        sql.execute(f"SELECT * FROM user_database WHERE id = {message.from_user.id}")
        print(sql.fetchall())

        await message.answer('Вы успешно подписались на рассылку!')
        await asyncio.sleep(1)
        await Main_menu(message, state)


async def promo(message: Message, state: FSMContext):

    promos = []
    sql.execute('''SELECT tag FROM tags''')
    for i in sql.fetchall():
        promos.append(i[0])

    if message.text == 'Отмена':

        mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        mailing_keyboard.add('Ввести промокод')
        mailing_keyboard.add('Подписаться')

        await message.answer('Хотите ввести промокод для эксклюзивной подписки?', reply_markup=mailing_keyboard)

        await Start_waiting_group.mailing_choice_2.set()

    elif message.text not in promos:
        await message.answer('Введенного промокода не существует!')
        return

    elif message.text in promos:

        sql.execute('''UPDATE user_database SET mailing = "exclusive"''')
        database.commit()

        sql.execute(f'''SELECT tag FROM tags WHERE tag = "{message.text}"''')
        tag = sql.fetchone()[0]

        sql.execute(f'''SELECT users FROM tags WHERE tag = "{message.text}"''')
        users = sql.fetchone()[0]
        if users == None:
            sql.execute(f'''UPDATE tags SET users = "{message.from_user.id}||" WHERE tag = "{tag}"''')
            database.commit()
        else:
            sql.execute(f'''UPDATE tags SET users = "{users}{message.from_user.id}||" WHERE tag = "{tag}"''')
            database.commit()


        await message.answer('Вы успешно подписались на эксклюзивную рассылку!')
        await asyncio.sleep(1)
        await Main_menu(message, state)






def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(mailing_choice, state=Start_waiting_group.mailing_choice_1)
    dp.register_message_handler(mailing_choice_next, state=Start_waiting_group.mailing_choice_2)
    dp.register_message_handler(promo, state=Start_waiting_group.waiting_promo)



