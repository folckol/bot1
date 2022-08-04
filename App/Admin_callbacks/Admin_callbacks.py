import asyncio
import sqlite3

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, Message

from Kwork_order_bot.App.All_user_handlers.Main_menu_handlers import Main_menu
from Kwork_order_bot.App.Classes.States_classes import Admin_waiting_group
from Kwork_order_bot.settings import TOKEN

database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\database.db')
sql = database.cursor()

admin_database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\admin_database.db')
admin_sql = admin_database.cursor()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)

async def admin_chatting(call: CallbackQuery, state: FSMContext):

    user_id = int(call.data.strip('answer_user_'))

    await state.update_data(user_b = user_id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отмена')

    await call.message.answer('Введите ответное сообщение пользователю', reply_markup=keyboard)
    await Admin_waiting_group.wait_admin_message.set()

async def wait_message_from_admin(message: Message, state: FSMContext):

    await state.update_data(message = message.text)

    keyboard  = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да', 'Нет')

    await message.answer('Вы уверены, что хотите отправить данное сообщение пользователю?\n\n'
                         f'{message.text}', reply_markup=keyboard)
    await Admin_waiting_group.admin_message_sending_confirm.set()


async def admin_message_send_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Нет']:
        await message.answer('Неверная комманда')
        return

    if message.text == 'Да':

        data = await state.get_data()

        try:
            await bot.send_message(chat_id=data['user_b'], text=f"Вам пришло сообщение от администратора:\n\n{data['message']}")
            await state.finish()
            await message.answer('Ваше сообщение было успешно отправлено!', reply_markup=ReplyKeyboardRemove())


        except:

            await state.finish()
            await message.answer('По каким то причинам, соощение не было отправлено', reply_markup=ReplyKeyboardRemove())


    if message.text == 'Нет':

        await state.finish()
        await message.answer('Отправка сообщения отменена', reply_markup=ReplyKeyboardRemove())


def register_callbacks(dp: Dispatcher):

    dp.register_callback_query_handler(admin_chatting, lambda x: 'answer_user_' in x.data,
                                       state='*')

    dp.register_message_handler(wait_message_from_admin, state=Admin_waiting_group.wait_admin_message)
    dp.register_message_handler(admin_message_send_confirm, state=Admin_waiting_group.admin_message_sending_confirm)



