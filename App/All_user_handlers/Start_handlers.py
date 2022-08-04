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

async def Start_message(message: Message, state: FSMContext):

    print(message.from_user.id)
    await state.finish()

    sql.execute(f"SELECT id FROM user_database WHERE id = ({message.from_user.id})")
    id = sql.fetchone()

    sql.execute(f"SELECT mailing FROM user_database WHERE id = ({message.from_user.id})")
    try:
        segmentation = sql.fetchone()[0]
    except:
        segmentation = None

    print(segmentation)

    print(id, segmentation)

    if id == 'None' or id == None:

        user_info = (message.from_user.id, 'None')
        sql.execute(f"INSERT INTO user_database VALUES (?,?)", user_info)
        database.commit()

        first_reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        first_reg_keyboard.add('Да', 'Нет')

        await message.answer('Хотите получать рассылку от нас?', reply_markup=first_reg_keyboard)

        await Start_waiting_group.mailing_choice_1.set()

    elif (segmentation == 'None'):
        await message.answer('Похоже, вы не завершили процесс регистрации. Пожалуйста завершите его.')

        first_reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        first_reg_keyboard.add('Да', 'Нет')

        await message.answer('Хотите получать рассылку от нас?', reply_markup=first_reg_keyboard)

        await Start_waiting_group.mailing_choice_1.set()

    else:

        await Main_menu(message, state)


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(Start_message, state='*', commands='start')


