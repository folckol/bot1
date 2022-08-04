import asyncio
import sqlite3

from aiogram import Dispatcher, types, Bot
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext

from Kwork_order_bot.App.Classes.States_classes import Start_waiting_group
from Kwork_order_bot.settings import admin_id, TOKEN

database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\database.db')
sql = database.cursor()

admin_database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\admin_database.db')
admin_sql = admin_database.cursor()

admin_id = admin_id[0]

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)

async def Main_menu(message: Message, state: FSMContext):

    await state.finish()

    admin_sql.execute('''SELECT text FROM main_menu_message WHERE id = (1)''')
    text = admin_sql.fetchone()[0]

    buttons = []
    admin_sql.execute("""SELECT title FROM questions""")
    for i in admin_sql.fetchall():
        buttons.append(str(i[0]))

    count = 0
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Персональный вопрос 📝')
    for i in buttons:
        keyboard.add(i)
        count += 1
        if count == 5:
            break

    if len(buttons) > 5:
        keyboard.add('➡️')

    await state.update_data(page=1)

    await message.answer(text, reply_markup=keyboard)
    await Start_waiting_group.main_menu_state.set()


async def Main_menu_choice(message: Message, state: FSMContext):

    data = await state.get_data()
    page = data['page']

    all_questions = []

    admin_sql.execute('''SELECT title FROM questions''')
    for i in admin_sql.fetchall():
        all_questions.append(i[0])

    page_quantity = len(all_questions) // 5
    if len(all_questions) % 5 != 0:
        page_quantity += 1

    print(page_quantity, page)

    if message.text in ['⬅️', '➡️']:
        try:
            if message.text == '⬅️':

                if page == 1:
                    await message.answer('Неверная команда')
                    return

                else:
                    next_page = page - 1
                    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add('Персональный вопрос 📝')

                    for mss in range(next_page*5 - 5, next_page*5):
                        try:
                            keyboard.add(all_questions[mss])
                        except:
                            pass

                    if next_page == 1:
                        keyboard.add('➡️')
                    elif next_page == page_quantity:
                        keyboard.add('⬅️')
                    else:
                        keyboard.add('⬅️', '➡️')

                    await state.update_data(msg=message.message_id,
                                            page=next_page)

                    admin_sql.execute('''SELECT text FROM main_menu_message WHERE id = (1)''')
                    text = admin_sql.fetchone()[0]
                    await message.answer(text, reply_markup=keyboard)
                    await Start_waiting_group.main_menu_state.set()

            if message.text == '➡️':

                if page == page_quantity:
                    await message.answer('Неверная команда')
                    return


                else:

                    next_page = page + 1
                    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add('Персональный вопрос 📝')

                    for mss in range(next_page*5 - 5, next_page*5):
                        try:
                            keyboard.add(all_questions[mss])
                        except:
                            pass

                    print('adadw')

                    if next_page == 1:
                        keyboard.add('➡️')
                    elif next_page == page_quantity:
                        keyboard.add('⬅️')
                    else:
                        keyboard.add('⬅️', '➡️')

                    await state.update_data(msg=message.message_id,
                                            page=next_page)

                    admin_sql.execute('''SELECT text FROM main_menu_message WHERE id = (1)''')
                    text = admin_sql.fetchone()[0]
                    await message.answer(text, reply_markup=keyboard)
                    await Start_waiting_group.main_menu_state.set()
        except:
            await message.answer('Неверная команда')
            return


    elif message.text not in all_questions:

        if message.text == 'Персональный вопрос 📝':

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Отмена')
            await message.answer('Напишите персональный вопрос администратору, он ответит вам в ближайшее время.', reply_markup=keyboard)
            await Start_waiting_group.waiting_admin_message.set()

        else:
            return


    elif message.text in all_questions:

        await state.update_data(title = message.text)

        admin_sql.execute(f'''SELECT subgroups FROM questions WHERE title = "{message.text}"''')
        subgroups = admin_sql.fetchone()[0]

        buttons = []
        for i in subgroups.split('||'):
            buttons.append(i.split(':::')[0])

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in buttons:
            keyboard.add(i)
        keyboard.add('Назад')

        await message.answer('Выберите подраздел', reply_markup=keyboard)
        await Start_waiting_group.subgroups_waiting.set()


async def Subgroups_menu_handler(message: Message, state: FSMContext):

    data = await state.get_data()

    all_subgroups = []
    admin_sql.execute(f'''SELECT subgroups FROM questions WHERE title = "{data['title']}"''')
    asa = admin_sql.fetchone()[0]
    for i in asa.split('||'):
        if i != '':
            all_subgroups.append(i)

    true_subgroup = None
    for i in all_subgroups:
        if message.text in i:
            true_subgroup = i

    if message.text == 'Назад':

        await Main_menu(message, state)

    elif true_subgroup != None:

        await message.answer(true_subgroup.split(':::')[1])
        await Start_waiting_group.subgroups_waiting.set()

    elif true_subgroup == None:
        await message.answer('Неверная команда')
        return

async def admin_message_send(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        await Main_menu(message, state)

    else:

        answer_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton('Ответить', callback_data=f'answer_user_{message.from_user.id}'))

        await bot.send_message(chat_id=admin_id,
                               text=f'Вопрос от пользователя <i>{message.from_user.id}</i>:\n\n{message.text}',
                               reply_markup=answer_keyboard)

        await message.answer('Ваш вопрос был успешно отправлен.')
        await Main_menu(message, state)


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(Main_menu)

    dp.register_message_handler(Main_menu_choice, state=Start_waiting_group.main_menu_state)
    dp.register_message_handler(Subgroups_menu_handler, state=Start_waiting_group.subgroups_waiting)
    dp.register_message_handler(admin_message_send, state=Start_waiting_group.waiting_admin_message)

