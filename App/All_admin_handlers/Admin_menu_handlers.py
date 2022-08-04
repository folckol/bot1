import asyncio
import os
import sqlite3

import pandas as pd
from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters import AdminFilter
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
    Document
from aiogram.dispatcher import FSMContext

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

from Kwork_order_bot.App.All_user_handlers.Main_menu_handlers import Main_menu
from Kwork_order_bot.App.Classes.States_classes import Start_waiting_group, Admin_waiting_group
from Kwork_order_bot.settings import TOKEN, admin_id

database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\database.db')
sql = database.cursor()

admin_database = sqlite3.connect(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\admin_database.db')
admin_sql = admin_database.cursor()


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)

async def Admin_menu(message: Message, state: FSMContext):
    # print(message.from_user.id)
    if message.from_user.id in admin_id:
        await state.finish()

        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()

async def variants(message: Message, state: FSMContext):

    if message.text not in ['Рассылка','Настроить частозадаваемые вопросы','Перейти в раздел промокодов','Выгрузить базу данных пользователей в формате Excel','Изменить приветственное сообщение','Выйти из панели админиcтратора', '/start']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Рассылка':

        mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        mailing_keyboard.add('Общая рассылка')
        mailing_keyboard.add('Рассылка по тэгам')
        mailing_keyboard.add('Рассылка по ID')
        mailing_keyboard.add('Назад')

        await message.answer('Выберите тип рассылки', reply_markup=mailing_keyboard)
        await Admin_waiting_group.choose_mailing_variant.set()

    if message.text == 'Настроить частозадаваемые вопросы':

        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()


    if message.text == 'Перейти в раздел промокодов':

        choose_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        choose_chapter_keyboard.add('Список промокодов')
        choose_chapter_keyboard.add('Добавить промокод')
        choose_chapter_keyboard.add('Удалить промокод')
        choose_chapter_keyboard.add('Назад')

        await message.answer('Выберите действие', reply_markup=choose_chapter_keyboard)
        await Admin_waiting_group.tags_promos.set()

    if message.text == 'Выгрузить базу данных пользователей в формате Excel':

        await message.answer('Таблица подготавливается, пожалуйста подождите.')

        all_users = []
        sql.execute(f"SELECT id FROM user_database")
        for i in sql.fetchall():
            all_users.append(i[0])


        sql.execute(f'''SELECT * FROM tags''')
        tags_info = sql.fetchall()

        all_tags = []

        for ff in all_users:
            tags = []

            for i in tags_info:
                if str(ff) in i[2].split('||'):
                    tags.append(i[1])

            if len(tags) == 0:

                all_tags.append('')

            else:

                tags_text = ''
                for i in tags:
                    tags_text+=f'{i}, '

                all_tags.append(tags_text)

        sql.execute(f"SELECT * FROM user_database")
        database_sql = sql.fetchall()

        ID = []
        mailing = []

        for i in database_sql:
            ID.append(i[0])
            mailing.append(i[1])

        wb = Workbook(write_only=True)
        ws = wb.create_sheet("Mysheet")

        ws.append(['ID', 'Вид рассылки', 'Тэги, привязанные к пользователю'])
        for i in range(100000):
            try:
                ws.append([str(ID[i]), str(mailing[i]), str(all_tags[i])])
            except:
                pass


        wb.save('C:/Users/Asus/PycharmProjects/Примеры работ/Kwork_order_bot/App/data/database.xlsx')


        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вот ваша база данных:', reply_markup=admin_menu_keyboard)
        await message.answer_document(
            document=open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\database.xlsx', 'rb'))

        if os.path.isfile(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\database.xlsx'):
            os.remove(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\database.xlsx')

        await state.finish()


        await Admin_waiting_group.admin_menu_waiting.set()

    if message.text == 'Изменить приветственное сообщение':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Назад')

        await message.answer('Отправьте новое приветственное сообщение', reply_markup=keyboard)
        await Admin_waiting_group.new_start_message.set()

    if message.text == 'Выйти из панели админиcтратора' or message.text == '/start':
        await Main_menu(message, state)


# НАСТРОЙКА РАССЫЛОК

async def mailing_settings(message: Message, state: FSMContext):

    if message.text not in ['Общая рассылка',
        'Рассылка по тэгам',
        'Рассылка по ID',
        'Назад']:

        await message.answer('Неверная команда')
        return

    if message.text == 'Назад':
        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()

    elif message.text == 'Общая рассылка':

        await state.update_data(mailing_type = 'default')

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отменить')

        await message.answer('Напишите текст рассылки или пришлите картинку', reply_markup=keyboard)
        await Admin_waiting_group.default_mailing_waiting_text.set()

    elif message.text == 'Рассылка по тэгам':

        await state.update_data(mailing_type='tags')

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отменить')

        await message.answer('Напишите тэги, по которым будет осуществлена рассылка в следующем формате:\n\n'
                             '<b>Тэг1:::Тэг2:::Тэг3...</b>', reply_markup=keyboard)
        await Admin_waiting_group.tags_mailing_settings.set()

    elif message.text == 'Рассылка по ID':

        await state.update_data(mailing_type='ids')

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Пришлите файл (.txt), в котором прописаны ID пользовователей через красную строку, например:\n\n'
                             '10000000\n'
                             '10000001\n'
                             '10000002\n'
                             '...', reply_markup=keyboard)
        await Admin_waiting_group.id_mailing_settings.set()


async def id_mailing_settings(message: Message, state: FSMContext):

    try:

        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        await bot.download_file(file_path, r"C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\file.txt")

        # await message.document.download(
        #     destination_dir=r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data',
        #     destination_file=f'file.txt')

        print('Скачано')

        users = []
        f = open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\file.txt', 'r')
        for i in f:
            users.append(i.strip('\n'))

        await state.update_data(users=users)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отменить')

        await message.answer('Напишите текст рассылки', reply_markup=keyboard)
        await Admin_waiting_group.default_mailing_waiting_text.set()


    except:

        if message.text == 'Отмена':

            mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            mailing_keyboard.add('Общая рассылка')
            mailing_keyboard.add('Рассылка по тэгам')
            mailing_keyboard.add('Рассылка по ID')
            mailing_keyboard.add('Назад')

            await message.answer('Выберите тип рассылки', reply_markup=mailing_keyboard)
            await Admin_waiting_group.choose_mailing_variant.set()

        else:
            await message.answer('Пришлите документ в правильном формате (file.txt)')
            return



async def mailing_tag_settings(message: Message, state: FSMContext):
    all_tags = []
    sql.execute('''SELECT tag FROM tags''')
    for i in sql.fetchall():
        all_tags.append(i[0])

    if message.text == 'Отменить':
        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()



    elif ':::' not in message.text:

        if message.text in all_tags:
            await state.update_data(tags=[message.text])

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Отменить')

            await message.answer(f'Ваш тэг: {message.text}.\nНапишите текст рассылки', reply_markup=keyboard)
            await Admin_waiting_group.default_mailing_waiting_text.set()

        else:
            print(all_tags)
            await message.answer('Тэги указаны в неверном формате.')
            return

    else:


        await state.update_data(tags = message.text.split(':::'))

        tags = message.text.split(':::')
        tags_text = ''
        for i in tags:
            if i == tags[-1]:
                tags_text+=i
            else:
                tags_text += i + ', '

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отменить')

        await message.answer(f'Ваши тэги: {tags_text}.\nНапишите текст рассылки', reply_markup=keyboard)
        await Admin_waiting_group.default_mailing_waiting_text.set()


async def default_mailing(message: Message, state: FSMContext):

    if message.text == 'Отменить':
        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()

    else:

        await state.update_data(mailing_text = message.text)

        try:
            await message.photo[-1].download(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg')
            await state.update_data(mailing_text=message.caption)
            await state.update_data(photo=True)
        except:
            await state.update_data(photo=False)

        default_mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        default_mailing_keyboard.add('Кнопка с ссылкой')
        default_mailing_keyboard.add('Цепочка сообщений')
        default_mailing_keyboard.add('Пропустить')
        default_mailing_keyboard.add('Отменить')

        await message.answer('Укажите дополнение к вашей рассылке.', reply_markup=default_mailing_keyboard)
        await Admin_waiting_group.default_mailing_waiting_next_action.set()

async def default_mailing_settings(message: Message, state: FSMContext):

    if message.text not in ['Кнопка с ссылкой',
        'Цепочка сообщений',
        'Пропустить',
        'Отменить']:

        await message.answer('Неверная команда')
        return

    if message.text == 'Отменить':

        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()

    else:

        if message.text == 'Кнопка с ссылкой':

            await state.update_data(message_chain = False)

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Назад')

            await message.answer('Пришлите название кнопки и ссылку в следующем формате: <b>название:::ссылка</b>\n\n'
                                 '<b>Пример</b>: Перейти:::https://google.com', reply_markup=keyboard)

            await Admin_waiting_group.default_mailing_waiting_link_button_setting.set()

        if message.text == 'Цепочка сообщений':
            await state.update_data(message_chain=True)
            await state.update_data(message_chain_list=[])

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Назад')

            await state.update_data(photo=False)

            await message.answer('Напишите 1 сообщение цепочки.\n\n'
                                 '<i><b>Примечание:</b> Если вы хотите добавить к тексту или картинке цепочки кнопку, пропишите её данные в следующем формате:</i>\n\n'
                                 'Гугл:::https://google.com (Кнопка, привязанная только к картинке)\n'
                                 'Добро пожаловать в яндекс|||Яндекс:::https://yandex.ru (Кнопка, привязанная к тексту или картинке с текстом)', reply_markup=keyboard)
            await Admin_waiting_group.default_mailing_waiting_message_chain_setting.set()

        if message.text == 'Пропустить':
            await state.update_data(message_chain=False)

            data = await state.get_data()

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Да', 'Нет')

            await message.answer(f'Вы уверены, что хотите отправить данное сообщение всем пользователям?')

            try:
                try:
                    with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg', 'rb') as photo:
                        await message.answer_photo(caption=data['mailing_text'],photo=photo, reply_markup=keyboard)
                except:
                    with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg', 'rb') as photo:
                        await message.answer_photo(photo=photo, reply_markup=keyboard)
            except:
                await message.answer(data['mailing_text'], reply_markup=keyboard)

            await Admin_waiting_group.default_mailing_waiting_confirm_sending.set()


async def default_mailing_add_link_button(message: Message, state: FSMContext):

    if message.text == 'Назад':

        default_mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        default_mailing_keyboard.add('Кнопка с ссылкой')
        default_mailing_keyboard.add('Цепочка сообщений')
        default_mailing_keyboard.add('Пропустить')
        default_mailing_keyboard.add('Отменить')

        await message.answer('Укажите дополнение к вашей рассылке.', reply_markup=default_mailing_keyboard)
        await Admin_waiting_group.default_mailing_waiting_next_action.set()

    else:

        if ':::' not in message.text or 'https' not in message.text:
            await message.answer('Вы неправильно ввели формат кнопки. Формат выглядит следующим образом:\n\n'
                                 '<b>название:::ссылка</b>')
            return

        else:

            button_name = message.text.split(':::')[0]
            button_link = message.text.split(':::')[1]

            await state.update_data(button_name = button_name,
                                    button_link = button_link)

            data = await state.get_data()

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Да', 'Нет')

            await message.answer(f'Вы уверены, что хотите отправить данное сообщение всем пользователям?', reply_markup=keyboard)

            try:
                try:
                    with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg', 'rb') as photo:
                        await message.answer_photo(caption=data['mailing_text'],photo=photo, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(button_name, url=button_link)))
                except:
                    with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg', 'rb') as photo:
                        await message.answer_photo(photo=photo, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(button_name, url=button_link)))
            except:
                await message.answer(data['mailing_text'], reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(button_name, url=button_link)))

            await Admin_waiting_group.default_mailing_waiting_confirm_sending.set()

async def default_mailing_add_message_chain(message: Message, state: FSMContext):

    if message.text == 'Назад':

        default_mailing_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        default_mailing_keyboard.add('Кнопка с ссылкой')
        default_mailing_keyboard.add('Цепочка сообщений')
        default_mailing_keyboard.add('Пропустить')
        default_mailing_keyboard.add('Отменить')

        await message.answer('Укажите дополнение к вашей рассылке.', reply_markup=default_mailing_keyboard)

        await Admin_waiting_group.default_mailing_waiting_next_action.set()

    elif message.text == 'Готово':

        data = await state.get_data()

        message_chain_list = data['message_chain_list']

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Да', 'Нет')

        await message.answer(f'Вы уверены, что хотите отправить эту цепочку сообщений всем пользователям?',
                             reply_markup=keyboard)
        await asyncio.sleep(1)
        for i in message_chain_list:

            i = i.split('|||')

            if len(i) == 1:
                await message.answer(i[0])
            elif len(i) == 2:
                if i[0] == 'None':
                    with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                              'rb') as photo:
                        await message.answer_photo(photo=photo)
                else:
                    with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                              'rb') as photo:
                        await message.answer_photo(photo=photo, caption=i[0])
            elif len(i) == 3:

                text = i[2].split(':::')[0]
                button = i[2].split(':::')[1]

                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                if i[1] != '...':

                    if i[0] == 'None':
                        with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                            await message.answer_photo(photo=photo, reply_markup=keyboard)
                    else:
                        with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                            await message.answer_photo(photo=photo, caption=i[0], reply_markup=keyboard)

                else:

                    text = i[2].split(':::')[0]
                    button = i[2].split(':::')[1]

                    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                    await message.answer(i[0], reply_markup=keyboard)

        await Admin_waiting_group.default_mailing_waiting_confirm_sending.set()

    elif message.text == 'Добавить сообщение':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Назад')

        await message.answer('Напишите следующее сообщение цепочки', reply_markup=keyboard)
        await Admin_waiting_group.default_mailing_waiting_message_chain_setting.set()

    else:

        data = await state.get_data()

        message_chain_list = data['message_chain_list']

        try:
            await message.photo[-1].download(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{len(data["message_chain_list"])+1}.jpg')

            if ':::' in message.caption:

                if '|||' in message.caption:

                    text = message.caption.split('|||')[1].split(':::')[0]
                    button = message.caption.split('|||')[1].split(':::')[1]

                    message_chain_list.append(f'{message.caption.split("|||")[0]}|||{len(data["message_chain_list"]) + 1}.jpg|||{text}:::{button}')
                    await state.update_data(message_chain_list=message_chain_list)
                    await state.update_data(photo=True)

                else:

                    text = message.caption.split(':::')[0]
                    button = message.caption.split(':::')[1]

                    message_chain_list.append(
                        f'None|||{len(data["message_chain_list"]) + 1}.jpg|||{text}:::{button}')
                    await state.update_data(message_chain_list=message_chain_list)
                    await state.update_data(photo=True)

            else:

                message_chain_list.append(f'{message.caption}|||{len(data["message_chain_list"])+1}.jpg')
                await state.update_data(message_chain_list=message_chain_list)
                await state.update_data(photo=True)

        except:
            if '|||' in message.text:

                text = message.text.split('|||')[1].split(':::')[0]
                button = message.text.split('|||')[1].split(':::')[1]

                message_chain_list.append(f'{message.text.split("|||")[0]}|||...|||{text}:::{button}')
                await state.update_data(message_chain_list=message_chain_list)

            else:
                message_chain_list.append(message.text)
                await state.update_data(message_chain_list = message_chain_list)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить сообщение')
        keyboard.add('Готово')
        keyboard.add('Назад')

        await message.answer('Ваша цепочка выглядит следующим образом:', reply_markup=keyboard)
        await asyncio.sleep(1)

        for i in message_chain_list:

            i = i.split('|||')

            if len(i) == 1:
                await message.answer(i[0])

            elif len(i) == 2:
                if i[0] == 'None':
                    with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                        await message.answer_photo(photo=photo)
                else:
                    with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                        await message.answer_photo(photo=photo, caption=i[0])

            elif len(i) == 3:

                text = i[2].split(':::')[0]
                button = i[2].split(':::')[1]

                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                if i[1] != '...':

                    if i[0] == 'None':
                        with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                            await message.answer_photo(photo=photo, reply_markup=keyboard)
                    else:
                        with open(fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}', 'rb') as photo:
                            await message.answer_photo(photo=photo, caption=i[0], reply_markup=keyboard)

                else:

                    text = i[2].split(':::')[0]
                    button = i[2].split(':::')[1]

                    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                    await message.answer(i[0], reply_markup=keyboard)



async def default_mailing_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Нет']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Нет':

        await Admin_menu(message, state)

    if message.text == 'Да':

        data = await state.get_data()

        # print(data)

        if data['mailing_type'] == 'default':

            message_link_button = False

            mailing_text = data['mailing_text']


            try:
                button_link = data['button_link']
                button_text = data['button_name']

                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=button_text, url=button_link))

                message_link_button = True
            except:
                pass

            sql.execute("""SELECT id FROM user_database WHERE mailing = 'default'""")
            all_users = []
            for i in sql.fetchall():
                all_users.append(i[0])

            sql.execute("""SELECT id FROM user_database WHERE mailing = 'exclusive'""")
            for i in sql.fetchall():
                all_users.append(i[0])

            if data['photo'] == False:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:
                                await bot.send_message(chat_id=id, text=msg)
                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text, reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text)
                        except:
                            pass

            elif data['photo'] == True:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:

                                i = msg.split('|||')

                                if len(i) == 1:
                                    await bot.send_message(chat_id=id, text=i[0])
                                elif len(i) == 2:
                                    if i[0] == 'None':
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo)
                                    else:
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo, caption=i[0])
                                elif len(i) == 3:

                                    text = i[2].split(':::')[0]
                                    button = i[2].split(':::')[1]

                                    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                                    if i[1] != '...':

                                        if i[0] == 'None':
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, reply_markup=keyboard)
                                        else:
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, caption=i[0],
                                                                           reply_markup=keyboard)

                                    else:

                                        text = i[2].split(':::')[0]
                                        button = i[2].split(':::')[1]

                                        keyboard = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(text=text, url=button))

                                        await bot.send_message(chat_id=id, text = i[0], reply_markup=keyboard)
                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text, reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text)
                        except:
                            pass

        elif data['mailing_type'] == 'tags':
            message_link_button = False

            mailing_text = data['mailing_text']

            try:
                button_link = data['button_link']
                button_text = data['button_name']

                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=button_text, url=button_link))

                message_link_button = True
            except:
                pass

            tag_set = data['tags']

            sql.execute("""SELECT * FROM tags""")
            tags = []
            for i in sql.fetchall():
                tags.append(i)

            print(tags)

            all_users = []

            for i in tag_set:

                for ii in tags:
                    if i == ii[1]:

                        for user in ii[2].split('||'):
                            if user not in all_users:
                                all_users.append(user)

            if data['photo'] == False:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:
                                await bot.send_message(chat_id=id, text=msg)
                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text, reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text)
                        except:
                            pass

            elif data['photo'] == True:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:
                                i = msg.split('|||')

                                if len(i) == 1:
                                    await bot.send_message(chat_id=id, text=i[0])
                                elif len(i) == 2:
                                    if i[0] == 'None':
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo)
                                    else:
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo, caption=i[0])
                                elif len(i) == 3:

                                    text = i[2].split(':::')[0]
                                    button = i[2].split(':::')[1]

                                    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                                    if i[1] != '...':

                                        if i[0] == 'None':
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, reply_markup=keyboard)
                                        else:
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, caption=i[0],
                                                                           reply_markup=keyboard)

                                    else:

                                        text = i[2].split(':::')[0]
                                        button = i[2].split(':::')[1]

                                        keyboard = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(text=text, url=button))

                                        await bot.send_message(chat_id=id, text = i[0], reply_markup=keyboard)
                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text,
                                                     reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text)
                        except:
                            pass

        elif data['mailing_type'] == 'ids':

            message_link_button = False

            mailing_text = data['mailing_text']

            try:
                button_link = data['button_link']
                button_text = data['button_name']

                keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=button_text, url=button_link))

                message_link_button = True
            except:
                pass


            all_users = data['users']

            if data['photo'] == False:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:
                                await bot.send_message(chat_id=id, text=msg)
                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text, reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            await bot.send_message(chat_id=id, text=mailing_text)
                        except:
                            pass

            elif data['photo'] == True:

                if data['message_chain'] == True:
                    for id in all_users:
                        for msg in data['message_chain_list']:
                            try:
                                i = msg.split('|||')

                                if len(i) == 1:
                                    await bot.send_message(chat_id=id, text=i[0])
                                elif len(i) == 2:
                                    if i[0] == 'None':
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo)
                                    else:
                                        with open(
                                                fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                'rb') as photo:
                                            await bot.send_photo(chat_id=id, photo=photo, caption=i[0])
                                elif len(i) == 3:

                                    text = i[2].split(':::')[0]
                                    button = i[2].split(':::')[1]

                                    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=text, url=button))

                                    if i[1] != '...':

                                        if i[0] == 'None':
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, reply_markup=keyboard)
                                        else:
                                            with open(
                                                    fr'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\{i[1]}',
                                                    'rb') as photo:
                                                await bot.send_photo(chat_id=id, photo=photo, caption=i[0],
                                                                           reply_markup=keyboard)

                                    else:

                                        text = i[2].split(':::')[0]
                                        button = i[2].split(':::')[1]

                                        keyboard = InlineKeyboardMarkup().add(
                                            InlineKeyboardButton(text=text, url=button))

                                        await bot.send_message(chat_id=id, text = i[0], reply_markup=keyboard)

                            except:
                                pass

                elif message_link_button == True:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text,
                                                     reply_markup=keyboard)
                        except:
                            pass

                else:
                    for id in all_users:
                        try:
                            with open(r'C:\Users\Asus\PycharmProjects\Примеры работ\Kwork_order_bot\App\data\0.jpg',
                                      'rb') as photo:
                                await bot.send_photo(chat_id=id, photo=photo, caption=mailing_text)
                        except:
                            pass

        await message.answer('Ваша рассылка была успешно осуществлена.')

        await Admin_menu(message, state)



# НАСТРОЙКА РАССЫЛОК
#
#


#
#
# НАСТРОЙКА ЧАСТОЗАДАВАЕМЫХ ВОПРОСОВ

async def questions_settings(message: Message, state: FSMContext):

    if message.text not in ['Добавить новый вопрос',
        'Редактировать вопрос',
        'Изменить порядок вопросов',
        'Удалить вопрос',
        'Назад']:

        await message.answer('Неверная команда')
        return

    if message.text == 'Добавить новый вопрос':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Введите название нового вопроса', reply_markup=keyboard)
        await Admin_waiting_group.new_question.set()

    if message.text == 'Редактировать вопрос':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Изменить название вопроса')
        keyboard.add('Изменить подразделы вопроса')
        keyboard.add('Отмена')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=keyboard)
        await Admin_waiting_group.edit_question.set()

    if message.text == 'Изменить порядок вопросов':

        buttons = []
        admin_sql.execute("""SELECT title FROM questions""")
        for i in admin_sql.fetchall():
            buttons.append(i[0])

        count = 0
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in buttons:
            keyboard.add(i)
            count += 1
            if count == 5:
                break

        if len(buttons) > 5:
            keyboard.add('Назад', '➡️')
        else:
            keyboard.add('Назад')

        await state.update_data(page=1)

        await message.answer('Выберите вопрос, порядок которого хотите изменить', reply_markup=keyboard)
        await Admin_waiting_group.edit_number_question.set()

    if message.text == 'Удалить вопрос':
        buttons = []
        admin_sql.execute("""SELECT title FROM questions""")
        for i in admin_sql.fetchall():
            buttons.append(str(i[0]))

        count = 0
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in buttons:
            keyboard.add(i)
            count += 1
            if count == 5:
                break

        if len(buttons) > 5:
            keyboard.add('Назад', '➡️')
        else:
            keyboard.add('Назад')

        await state.update_data(page=1)

        await message.answer('Выберите вопрос, который хотите удалить', reply_markup=keyboard)
        await Admin_waiting_group.delete_question.set()


    if message.text == 'Назад':
        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()


async def new_question(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    else:

        await state.update_data(question_name = message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Сколько подразделов к вопросу вы хотите добавить? (укажите цифрой)', reply_markup=keyboard)

        await Admin_waiting_group.new_question_wait_number.set()

async def wait_quantity_subgroups(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    else:

        try:
            number = int(message.text)
            await state.update_data(end_quantity = number)
            await state.update_data(start_quantity = 1)

        except:
            await message.answer('Количество подразделов может быть указано только цифрой')
            return

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Пропишите название подраздела номер 1 и текст к нему в следующем формате: <b>название:::текст</b>.\n\n'
                             '<b>Например:</b> Автодром:::Наши контакты...', reply_markup=keyboard)
        await Admin_waiting_group.new_question_wait_text_description.set()

async def new_question_add_subgroups(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    if ':::' not in message.text:
        await message.answer('Укажите правильный формат подраздела')
        return

    subgroup_title = message.text.split(':::')[0]
    subgroup_text = message.text.split(':::')[1]

    await state.update_data(subgroup_text = subgroup_text,
                            subgroup_title = subgroup_title)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да', 'Изменить')

    await message.answer('Ваш подраздел будет выглядеть следующим образом:\n\n'
                         f'<i>Кнопка:</i> {subgroup_title}\n\n'
                         f'<i>Выдаваемый текст:</i>\n{subgroup_text}', reply_markup=keyboard)
    await Admin_waiting_group.new_question_confirm.set()


async def new_question_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Изменить']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Да':
        data = await state.get_data()

        f = 0
        admin_sql.execute("""SELECT id FROM questions""")
        for ff in admin_sql.fetchall():
            f = ff[0]
        f+=1

        success = False
        admin_sql.execute("""SELECT title FROM questions""")
        for i in admin_sql.fetchall():
            if i[0] == data['question_name']:
                admin_sql.execute(f"""SELECT subgroups FROM questions WHERE title = '{i[0]}'""")
                subgroups = admin_sql.fetchone()[0]

                admin_sql.execute(f"""UPDATE questions SET subgroups = '{subgroups+"||"+data['subgroup_title']+":::"+data['subgroup_text']}'""")
                admin_database.commit()

                success = True

                break

        if success == False:

            question_data = (f, data['question_name'], f"{data['subgroup_title']}:::{data['subgroup_text']}")

            admin_sql.execute("""INSERT INTO questions VALUES (?,?,?)""", question_data)
            admin_database.commit()


        if data['start_quantity'] < data['end_quantity']:

            await state.update_data(start_quantity = data['start_quantity']+1)

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Отмена')

            await message.answer('Ваш подраздел успешно добавлен!')

            await message.answer(
                f'Пропишите название подраздела номер {data["start_quantity"]+1} и текст к нему в следующем формате: <b>название:::текст</b>.\n\n'
                '<b>Например:</b> Автодром:::Наши контакты...', reply_markup=keyboard)
            await Admin_waiting_group.new_question_wait_text_description.set()

        else:
            await message.answer('Все прописанные подразделы успешно добавлены!')
            await Admin_menu(message, state)

    if message.text == 'Изменить':

        data = await state.get_data()

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer(
            f'Пропишите название подраздела номер {data["start_quantity"]} и текст к нему в следующем формате: <b>название:::текст</b>.\n\n'
            '<b>Например:</b> Автодром:::Наши контакты...', reply_markup=keyboard)
        await Admin_waiting_group.new_question_wait_text_description.set()


async def edit_question(message: Message, state: FSMContext):

    if message.text not in ['Изменить название вопроса',
        'Изменить подразделы вопроса',
        'Отмена']:

        await message.answer('Неверная команда')
        return

    if message.text == 'Отмена':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    else:
        buttons = []
        admin_sql.execute("""SELECT title FROM questions""")
        for i in admin_sql.fetchall():
            buttons.append(i[0])

        count = 0
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for i in buttons:
            keyboard.add(i)
            count += 1
            if count == 5:
                break

        if len(buttons) > 5:
            keyboard.add('Назад', '➡️')
        else:
            keyboard.add('Назад')

        await state.update_data(action = message.text)
        await state.update_data(page = 1)

        await message.answer('Выберите вопрос, который хотите отредактировать', reply_markup=keyboard)
        await Admin_waiting_group.waiting_choose_question.set()

async def edit_questions_choose_subgroup(message: Message, state: FSMContext):

    data = await state.get_data()
    page = data['page']

    titles = []
    admin_sql.execute("""SELECT title FROM questions""")
    for i in admin_sql.fetchall():
        titles.append(i[0])

    page_quantity = len(titles) // 5
    if len(titles)%5!=0:
        page_quantity+=1


    if message.text not in titles and message.text not in ['⬅️','Назад', '➡️']:
            await message.answer('Неверная команда')
            return

    if message.text in titles:

        if data['action'] == 'Изменить название вопроса':

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Назад')

            await state.update_data(title = message.text)
            await message.answer(f'Введите новое название для вопроса <i>{message.text}</i>', reply_markup=keyboard)
            await Admin_waiting_group.edit_question_edit_name.set()

        elif data['action'] == 'Изменить подразделы вопроса':

            # admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{message.text}'")
            # subgroups_data = admin_sql.fetchone()[0]
            #
            # all_subgroups = []
            # for i in subgroups_data.split('||'):
            #     all_subgroups.append({'title': i.split(':::')[0],
            #                           'text': i.split(':::')[1]})
            #
            # for i in all_subgroups:
            #     keyboard.add(i['title'])

            await state.update_data(title=message.text)

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Добавить раздел')
            keyboard.add('Удалить раздел')
            keyboard.add('Изменить название')
            keyboard.add('Изменить текст')
            keyboard.add('Назад')

            await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
            await Admin_waiting_group.edit_question_edit_subgroups.set()

    if message.text in ['⬅️','Назад', '➡️']:

        if message.text == '⬅️':

            if page == 1:
                await message.answer('Неверная команда')
                return

            else:

                next_page = page-1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️','Назад', '➡️')



                await state.update_data(msg = message.message_id,
                                        page = next_page)

                await message.answer('Выберите вопрос, который хотите отредактировать', reply_markup=keyboard)

                await Admin_waiting_group.waiting_choose_question.set()

        if message.text == '➡️':

            print(page, page_quantity)

            if page == page_quantity:
                await message.answer('Неверная команда')
                return

            else:
                next_page = page + 1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️', 'Назад', '➡️')



                await state.update_data(msg=message.message_id,
                                        page=next_page)

                await message.answer('Выберите вопрос, который хотите отредактировать', reply_markup=keyboard)


                await Admin_waiting_group.waiting_choose_question.set()

        if message.text == 'Назад':
            questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            questions_settings_keyboard.add('Добавить новый вопрос')
            questions_settings_keyboard.add('Редактировать вопрос')
            questions_settings_keyboard.add('Изменить порядок вопросов')
            questions_settings_keyboard.add('Удалить вопрос')
            questions_settings_keyboard.add('Назад')

            await message.answer('Выберите действие, которое хотите осуществить',
                                 reply_markup=questions_settings_keyboard)
            await Admin_waiting_group.choose_questions_settings.set()

async def edit_question_title(message: Message, state: FSMContext):

    if message.text == 'Назад':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()


    data = await state.get_data()
    title = data['title']

    await state.update_data(new_title = message.text)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да', 'Нет')

    await message.answer(f'Вы уверены, что хотите изменить название вопроса <i>{title}</i> на <i>{message.text}</i>?',reply_markup=keyboard)
    await Admin_waiting_group.edit_question_edit_name_confirm.set()


async def edit_question_title_confirm(message: Message, state: FSMContext):

    if message.text not in ['Нет', 'Да']:
        await message.answer('Неверная комманда')
        return

    if message.text == 'Нет':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    if message.text == 'Да':

        data = await state.get_data()
        title = data['title']
        new_title = data['new_title']

        admin_sql.execute(f'''UPDATE questions SET title = "{new_title}" WHERE title = "{title}"''')
        admin_database.commit()

        await message.answer('Название вопроса было успешно изменено!')
        await Admin_menu(message, state)


#
# НАСТРОЙКА ПОДРАЗДЕЛОВ

async def edit_subgroups(message: Message, state: FSMContext):

    if message.text not in ['Добавить раздел',
        'Удалить раздел',
        'Изменить название',
        'Изменить текст',
        'Назад']:

        await message.answer('Неверная комманда')
        return


    if message.text == 'Добавить раздел':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Пропишите название подраздела номер "номер по счету" и текст к нему в следующем формате: <b>название:::текст</b>.\n\n'
                             '<b>Например:</b> Автодром:::Наши', reply_markup=keyboard)
        await Admin_waiting_group.new_subgroup.set()

    if message.text == 'Удалить раздел':

        data = await state.get_data()

        admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
        subgroups_data = admin_sql.fetchone()[0]

        all_subgroups = []
        for i in subgroups_data.split('||'):
            all_subgroups.append({'title': i.split(':::')[0],
                                  'text': i.split(':::')[1]})

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        for i in all_subgroups:
            keyboard.add(i['title'])

        keyboard.add('Отмена')

        await message.answer('Выберите подраздел, который хотите удалить', reply_markup=keyboard)
        await Admin_waiting_group.delete_subgroup.set()

    if message.text == 'Изменить название':

        data = await state.get_data()

        admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
        subgroups_data = admin_sql.fetchone()[0]

        all_subgroups = []
        for i in subgroups_data.split('||'):
            all_subgroups.append({'title': i.split(':::')[0],
                                  'text': i.split(':::')[1]})

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        for i in all_subgroups:
            keyboard.add(i['title'])

        keyboard.add('Отмена')

        await message.answer('Выберите подраздел, название которого хотите изменить', reply_markup=keyboard)
        await Admin_waiting_group.edit_subgroup_title.set()

    if message.text == 'Изменить текст':
        data = await state.get_data()

        admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
        subgroups_data = admin_sql.fetchone()[0]

        all_subgroups = []
        for i in subgroups_data.split('||'):
            all_subgroups.append({'title': i.split(':::')[0],
                                  'text': i.split(':::')[1]})

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        for i in all_subgroups:
            keyboard.add(i['title'])

        keyboard.add('Отмена')

        await message.answer('Выберите подраздел, текст которого хотите изменить', reply_markup=keyboard)
        await Admin_waiting_group.edit_subgroup_text.set()

    if message.text == 'Назад':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить', reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()


async def new_subgroup(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    subgroup_title = message.text.split(':::')[0]
    subgroup_text = message.text.split(':::')[1]

    await state.update_data(subgroup_title = subgroup_title,
                            subgroup_text = subgroup_text)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да', 'Изменить')

    await message.answer('Ваш подраздел будет выглядить следующим образом:\n\n'
                         f'{subgroup_title}\n\n'
                         f'{subgroup_text}', reply_markup=keyboard)
    await Admin_waiting_group.new_subgroup_confirm.set()

async def new_subgroup_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Изменить']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Да':

        data = await state.get_data()

        admin_sql.execute(f"""SELECT subgroups FROM questions WHERE title = '{data["title"]}'""")
        text = admin_sql.fetchone()[0]

        text = text + '||' + data['subgroup_title'] + ':::' + data['subgroup_text']

        admin_sql.execute(f"""UPDATE questions SET subgroups = '{text}' WHERE title = '{data["title"]}'""")
        admin_database.commit()

        await message.answer('Ваш подраздел был успешно добавлен')
        await Admin_menu(message, state)

    if message.text == 'Изменить':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer(
            'Пропишите название подраздела номер "номер по счету" и текст к нему в следующем формате: <b>название:::текст</b>.\n\n'
            '<b>Например:</b> Автодром:::Наши', reply_markup=keyboard)
        await Admin_waiting_group.new_subgroup.set()

async def delete_subgroup(message: Message, state: FSMContext):

    data = await state.get_data()

    admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
    subgroups_data = admin_sql.fetchone()[0]

    all_subgroups = []
    for i in subgroups_data.split('||'):
        all_subgroups.append({'title': i.split(':::')[0],
                              'text': i.split(':::')[1]})

    subgroups = []
    for i in all_subgroups:
        subgroups.append(i['title'])

    if message.text not in subgroups and message.text != 'Отмена':
        await message.answer('Неверная команда')
        return

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    if message.text in subgroups:

        await state.update_data(subgroup_title = message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Да', 'Нет')

        await message.answer('Вы уверены, что хотите удалить выбранный раздел?', reply_markup=keyboard)
        await Admin_waiting_group.delete_subgroup_confirm.set()


async def delete_subgroup_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Нет']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Да':
        data = await state.get_data()
        title = data['subgroup_title']

        admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
        subgroups_data = admin_sql.fetchone()[0]

        all_subgroups = []
        for i in subgroups_data.split('||'):
            all_subgroups.append({'title': i.split(':::')[0],
                                  'text': i.split(':::')[1]})

        count = 0
        for i in all_subgroups:
            if i['title'] == title:
                break
            count+=1
        all_subgroups.pop(count)

        text = ''
        for i in all_subgroups:
            text+=f"{i['title']}:::{i['text']}"
            if i != all_subgroups[-1]:
                text+='||'

        admin_sql.execute(f"UPDATE questions SET subgroups = '{text}' WHERE title = '{data['''title''']}'")
        admin_database.commit()

        await message.answer('Подраздел был успешно удален')
        await Admin_menu(message, state)

    if message.text == 'Нет':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()


async def edit_subgroup_title(message: Message, state: FSMContext):
    data = await state.get_data()

    admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
    subgroups_data = admin_sql.fetchone()[0]

    all_subgroups = []
    for i in subgroups_data.split('||'):
        all_subgroups.append({'title': i.split(':::')[0],
                              'text': i.split(':::')[1]})

    subgroups = []
    for i in all_subgroups:
        subgroups.append(i['title'])

    if message.text not in subgroups and message.text != 'Отмена':
        await message.answer('Неверная команда')
        return

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    if message.text in subgroups:
        await state.update_data(subgroup_title=message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Введите новое название для выбранного подраздела', reply_markup=keyboard)
        await Admin_waiting_group.edit_subgroup_title_confirm.set()


async def edit_subgroup_title_confirm(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    data = await state.get_data()
    title = data['subgroup_title']

    admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
    subgroups_data = admin_sql.fetchone()[0]

    all_subgroups = []
    for i in subgroups_data.split('||'):
        all_subgroups.append({'title': i.split(':::')[0],
                              'text': i.split(':::')[1]})

    for i in all_subgroups:
        if i['title'] == title:
            i['title'] = message.text
            break

    text = ''
    for i in all_subgroups:
        text += f"{i['title']}:::{i['text']}"
        if i != all_subgroups[-1]:
            text += '||'

    admin_sql.execute(f"UPDATE questions SET subgroups = '{text}' WHERE title = '{data['''title''']}'")
    admin_database.commit()

    await message.answer('Название подраздела было успешно изменено')
    await Admin_menu(message, state)

async def edit_subgroup_text(message: Message, state: FSMContext):
    data = await state.get_data()

    admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
    subgroups_data = admin_sql.fetchone()[0]

    all_subgroups = []
    for i in subgroups_data.split('||'):
        all_subgroups.append({'title': i.split(':::')[0],
                              'text': i.split(':::')[1]})

    subgroups = []
    for i in all_subgroups:
        subgroups.append(i['title'])

    if message.text not in subgroups and message.text != 'Отмена':
        await message.answer('Неверная команда')
        return

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    if message.text in subgroups:
        await state.update_data(subgroup_title=message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Введите новый текст для выбранного подраздела', reply_markup=keyboard)
        await Admin_waiting_group.edit_subgroup_text_confirm.set()


async def edit_subgroup_text_confirm(message: Message, state: FSMContext):

    if message.text == 'Отмена':
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Добавить раздел')
        keyboard.add('Удалить раздел')
        keyboard.add('Изменить название')
        keyboard.add('Изменить текст')
        keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите выполнить с подразделом', reply_markup=keyboard)
        await Admin_waiting_group.edit_question_edit_subgroups.set()

    data = await state.get_data()
    title = data['subgroup_title']

    admin_sql.execute(f"SELECT subgroups FROM questions WHERE title = '{data['''title''']}'")
    subgroups_data = admin_sql.fetchone()[0]

    all_subgroups = []
    for i in subgroups_data.split('||'):
        all_subgroups.append({'title': i.split(':::')[0],
                              'text': i.split(':::')[1]})

    for i in all_subgroups:
        if i['title'] == title:
            i['text'] = message.text
            break

    text = ''
    for i in all_subgroups:
        text += f"{i['title']}:::{i['text']}"
        if i != all_subgroups[-1]:
            text += '||'

    admin_sql.execute(f"UPDATE questions SET subgroups = '{text}' WHERE title = '{data['''title''']}'")
    admin_database.commit()

    await message.answer('Текст подраздела был успешно изменен')
    await Admin_menu(message, state)

# НАСТРОЙКА ПОДРАЗДЕЛОВ
#


async def edit_question_number(message: Message, state: FSMContext):
    data = await state.get_data()
    page = data['page']

    titles = []
    admin_sql.execute("""SELECT title FROM questions""")
    for i in admin_sql.fetchall():
        titles.append(i[0])

    page_quantity = len(titles) // 5
    if len(titles) % 5 != 0:
        page_quantity += 1

    if message.text not in titles and message.text not in ['⬅️', 'Назад', '➡️']:
        await message.answer('Неверная команда')
        return

    if message.text in titles:


        await state.update_data(title = message.text)

        all_ids = []
        admin_sql.execute(f'''SELECT id FROM questions''')
        for i in admin_sql.fetchall():
             all_ids.append(i[0])

        admin_sql.execute(f'''SELECT id FROM questions WHERE title = "{message.text}"''')
        real_id = admin_sql.fetchone()[0]

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        if real_id  == 1:
            if all_ids[-1] > 1:
                keyboard.add('Назад', '⬇️')
            else:
                keyboard.add('Назад')

        elif real_id == all_ids[-1]:
            keyboard.add( '⬆️', 'Назад')

        else:
            keyboard.add('⬆️', 'Назад', '⬇️')

        await message.answer('Укажите, куда сместить выбранный вопрос', reply_markup=keyboard)
        await Admin_waiting_group.edit_number_question_confirm.set()


    if message.text in ['⬅️', 'Назад', '➡️']:

        if message.text == '⬅️':

            if page == 1:
                await message.answer('Неверная команда')
                return

            else:

                next_page = page - 1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️', 'Назад', '➡️')

                await message.answer('Укажите, куда сместить выбранный вопрос', reply_markup=keyboard)

                await state.update_data(msg=message.message_id,
                                        page=next_page)


                await Admin_waiting_group.edit_number_question.set()

        if message.text == '➡️':

            if page == page_quantity:
                await message.answer('Неверная команда')
                return

            else:
                next_page = page + 1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️', 'Назад', '➡️')



                await state.update_data(msg=message.message_id,
                                        page=next_page)

                await message.answer('Укажите, куда сместить выбранный вопрос', reply_markup=keyboard)

                await Admin_waiting_group.edit_number_question.set()

        if message.text == 'Назад':
            questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            questions_settings_keyboard.add('Добавить новый вопрос')
            questions_settings_keyboard.add('Редактировать вопрос')
            questions_settings_keyboard.add('Изменить порядок вопросов')
            questions_settings_keyboard.add('Удалить вопрос')
            questions_settings_keyboard.add('Назад')

            await message.answer('Выберите действие, которое хотите осуществить',
                                 reply_markup=questions_settings_keyboard)
            await Admin_waiting_group.choose_questions_settings.set()


async def edit_question_number_confirm(message: Message, state: FSMContext):

    if message.text not in ['⬆️', 'Назад', '⬇️']:
        await message.answer('Неверная команда')
        return


    data = await state.get_data()
    title = data['title']

    all_ids = []
    admin_sql.execute(f'''SELECT id FROM questions''')
    for i in admin_sql.fetchall():
        all_ids.append(i[0])

    admin_sql.execute(f'''SELECT id FROM questions WHERE title = "{title}"''')
    real_id = admin_sql.fetchone()[0]

    if real_id == all_ids[0] and message.text == '⬆️':

        await message.answer('Неверная команда')
        return

    elif real_id == all_ids[-1] and message.text == '⬇️':

        await message.answer('Неверная команда')
        return

    elif message.text == 'Назад':
        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить',
                             reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()

    else:

        if message.text == '⬆️':

            real_title_data = {"id": None,
                               "title": None,
                               "subgroups": None}

            admin_sql.execute(f'''SELECT * FROM questions WHERE id = ({real_id})''')
            count = 0
            for i in admin_sql.fetchall()[0]:

                if count == 0:
                    real_title_data['id'] = i
                if count == 1:
                    real_title_data['title'] = i
                if count == 2:
                    real_title_data['subgroups'] = i
                count += 1

            print(real_title_data)

            new_title_data = {"id": None,
                              "title": None,
                              "subgroups": None}

            admin_sql.execute(f'''SELECT * FROM questions WHERE id = ({real_id - 1})''')

            count = 0
            for i in admin_sql.fetchall()[0]:

                if count == 0:
                    new_title_data['id'] = i
                if count == 1:
                    new_title_data['title'] = i
                if count == 2:
                    new_title_data['subgroups'] = i
                count += 1

            admin_sql.execute(f'''UPDATE questions SET title = "{real_title_data['title']}", subgroups = "{real_title_data['subgroups']}" WHERE id = ({real_id-1})''')
            admin_database.commit()

            admin_sql.execute(
                f'''UPDATE questions SET title = "{new_title_data['title']}", subgroups = "{new_title_data['subgroups']}" WHERE id = ({real_id})''')
            admin_database.commit()

        elif message.text == '⬇️':
            real_title_data = {"id": None,
                               "title": None,
                               "subgroups": None}

            admin_sql.execute(f'''SELECT * FROM questions WHERE id = ({real_id})''')
            count = 0
            for i in admin_sql.fetchall()[0]:
                print(i)
                if count == 0:
                    real_title_data['id'] = i
                if count == 1:
                    real_title_data['title'] = i
                if count == 2:
                    real_title_data['subgroups'] = i
                count+=1

            new_title_data = {"id": None,
                               "title": None,
                               "subgroups": None}

            admin_sql.execute(f'''SELECT * FROM questions WHERE id = ({real_id + 1})''')

            count = 0
            for i in admin_sql.fetchall()[0]:
                if count == 0:
                    new_title_data['id'] = i
                if count == 1:
                    new_title_data['title'] = i
                if count == 2:
                    new_title_data['subgroups'] = i
                count += 1


            admin_sql.execute(
                f'''UPDATE questions SET title = "{real_title_data['title']}", subgroups = "{real_title_data['subgroups']}" WHERE id = ({real_id + 1})''')
            admin_database.commit()

            admin_sql.execute(
                f'''UPDATE questions SET title = "{new_title_data['title']}", subgroups = "{new_title_data['subgroups']}" WHERE id = ({real_id})''')
            admin_database.commit()

        await message.answer('Вы успешно изменили номер выбранного вопроса.')
        await Admin_menu(message, state)


async def delete_question(message: Message, state: FSMContext):
    data = await state.get_data()
    page = data['page']

    titles = []
    admin_sql.execute("""SELECT title FROM questions""")
    for i in admin_sql.fetchall():
        titles.append(i[0])

    page_quantity = len(titles) // 5
    if len(titles) % 5 != 0:
        page_quantity += 1

    if message.text not in titles and message.text not in ['⬅️', 'Назад', '➡️']:
        await message.answer('Неверная команда')
        return

    if message.text in titles:

        await state.update_data(title = message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Да', 'Нет')

        await message.answer('Вы уверены, что хотите удалить выбранный вопрос?', reply_markup=keyboard)
        await Admin_waiting_group.delete_question_confirm.set()


    if message.text in ['⬅️', 'Назад', '➡️']:

        if message.text == '⬅️':

            if page == 1:
                await message.answer('Неверная команда')
                return

            else:

                next_page = page - 1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️', 'Назад', '➡️')



                await state.update_data(msg=message.message_id,
                                        page=next_page)

                await message.answer('Выберите вопрос, который хотите удалить', reply_markup=keyboard)

                await Admin_waiting_group.delete_question.set()

        if message.text == '➡️':

            if page == page_quantity:
                await message.answer('Неверная команда')
                return

            else:
                next_page = page + 1

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

                for mss in range(next_page*5 - 5, next_page*5):
                    try:
                        keyboard.add(titles[mss])
                    except:
                        pass

                if next_page == 1:
                    keyboard.add('Назад', '➡️')
                elif next_page == page_quantity:
                    keyboard.add('⬅️', 'Назад')
                else:
                    keyboard.add('⬅️', 'Назад', '➡️')



                await state.update_data(msg=message.message_id,
                                        page=next_page)

                await message.answer('Выберите вопрос, который хотите удалить', reply_markup=keyboard)


                await Admin_waiting_group.delete_question.set()

        if message.text == 'Назад':
            questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            questions_settings_keyboard.add('Добавить новый вопрос')
            questions_settings_keyboard.add('Редактировать вопрос')
            questions_settings_keyboard.add('Изменить порядок вопросов')
            questions_settings_keyboard.add('Удалить вопрос')
            questions_settings_keyboard.add('Назад')

            await message.answer('Выберите действие, которое хотите осуществить',
                                 reply_markup=questions_settings_keyboard)
            await Admin_waiting_group.choose_questions_settings.set()

async def delete_question_confirm(message: Message, state: FSMContext):

    if message.text not in ['Да', 'Нет']:
        await message.answer('Неверная команда')
        return

    data = await state.get_data()

    if message.text == 'Да':

        admin_sql.execute(f'''SELECT id FROM questions WHERE title = "{data['title']}"''')
        id = admin_sql.fetchone()[0]

        admin_sql.execute(f'''DELETE FROM questions WHERE title = "{data['title']}"''')
        admin_database.commit()

        admin_sql.execute(f'''SELECT id FROM questions''')
        data = admin_sql.fetchall()
        print(data)

        last_id = data[-1][0]

        print(last_id, id)

        if last_id > id:
            for i in range(id, last_id):
                print(i)
                admin_sql.execute(f'''UPDATE questions SET id = ({i}) WHERE id = ({i+1})''')
                admin_database.commit()

        await message.answer('Выбранный вопрос был успешно удален!')
        await Admin_menu(message, state)

    if message.text == 'Нет':

        questions_settings_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        questions_settings_keyboard.add('Добавить новый вопрос')
        questions_settings_keyboard.add('Редактировать вопрос')
        questions_settings_keyboard.add('Изменить порядок вопросов')
        questions_settings_keyboard.add('Удалить вопрос')
        questions_settings_keyboard.add('Назад')

        await message.answer('Выберите действие, которое хотите осуществить',
                             reply_markup=questions_settings_keyboard)
        await Admin_waiting_group.choose_questions_settings.set()


# НАСТРОЙКА ЧАСТОЗАДАВАЕМЫХ ВОПРОСОВ
#
#



#
#
# НАСТРОЙКА СТАРТОВОГО ПРЕДЛОЖЕНИЯ

async def new_start_message(message: Message, state: FSMContext):

    if message.text == 'Назад':
        await state.finish()

        admin_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        admin_menu_keyboard.add('Рассылка')
        admin_menu_keyboard.add('Изменить приветственное сообщение')
        admin_menu_keyboard.add('Настроить частозадаваемые вопросы')
        admin_menu_keyboard.add('Перейти в раздел промокодов')
        admin_menu_keyboard.add('Выгрузить базу данных пользователей в формате Excel')
        admin_menu_keyboard.add('Выйти из панели админиcтратора')

        await message.answer('Вы находитесь в панели администратора', reply_markup=admin_menu_keyboard)
        await Admin_waiting_group.admin_menu_waiting.set()

    else:

        await state.update_data(new_message_text = message.text)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Подтвердить', 'Изменить')

        await message.answer(f'Ваше новое приветственное сообщение будет выглядеть следующим образом:\n\n{message.text}', reply_markup=keyboard)
        await Admin_waiting_group.new_start_message_confirm.set()


async def new_start_message_confirm(message: Message, state: FSMContext):
    if message.text not in ['Подтвердить', 'Изменить']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Подтвердить':

        data = await state.get_data()

        admin_sql.execute(f'''UPDATE main_menu_message SET text = "{data['new_message_text']}" WHERE id = (1)''')
        admin_database.commit()

        await message.answer('Вы успешно изменили приветственное сообщение')
        await Admin_menu(message, state)

    if message.text == 'Изменить':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Назад')

        await message.answer('Отправьте новое приветственное сообщение', reply_markup=keyboard)
        await Admin_waiting_group.new_start_message.set()





# НАСТРОЙКА СТАРТОВОГО ПРЕДЛОЖЕНИЯ
#
#



#
#
# НАСТРОЙКА ТЭГОВ И ПРОМОКОДОВ


async def promos_settings(message: Message, state: FSMContext):

    if message.text not in ['Список промокодов','Удалить промокод','Добавить промокод', 'Назад']:
        await message.answer('Неверная команда')
        return

    if message.text == 'Добавить промокод':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Отмена')

        await message.answer('Введите название промокода', reply_markup=keyboard)

        # await message.answer('Введите название одного или нескольких тэгов, к которым будет привязан промокод', reply_markup=keyboard)
        await Admin_waiting_group.new_promo.set()

    if message.text == 'Удалить промокод':

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Список промокодов')
        keyboard.add('Отмена')

        await message.answer('Введите название промокода, который хотите удалить', reply_markup=keyboard)
        await Admin_waiting_group.delete_promo.set()

    if message.text == 'Список промокодов':

        promos = []
        sql.execute('''SELECT tag FROM tags''')
        for i in sql.fetchall():
            promos.append(i[0])

        text = ''
        for i in promos:
            text += i + ' '
            if i != promos[-1]:
                text += '| '

        await message.answer(f'<i>Вот список всех существующих на данный момент промокодов:</i>\n\n{text}')
        await Admin_waiting_group.tags_promos.set()

    if message.text == 'Назад':

        await Admin_menu(message, state)

async def new_promo(message: Message, state: FSMContext):

    last_number = 1
    sql.execute('''SELECT id FROM tags''')
    for i in sql.fetchall():
        last_number = i[0]

    values = (last_number, message.text, '')

    sql.execute("INSERT INTO tags VALUES (?, ?, ?)", values)
    database.commit()

    choose_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    choose_chapter_keyboard.add('Список промокодов')
    choose_chapter_keyboard.add('Добавить промокод')
    choose_chapter_keyboard.add('Удалить промокод')
    choose_chapter_keyboard.add('Назад')

    await message.answer('Новый промокод был успешно добавлен!', reply_markup=choose_chapter_keyboard)
    await Admin_waiting_group.tags_promos.set()

async def delete_promo(message: Message, state: FSMContext):

    if message.text == 'Список промокодов':
        tags = []
        sql.execute('''SELECT tag FROM tags''')
        for i in sql.fetchall():
            tags.append(i[0])

        text = ''
        for i in tags:
            text += i + ' '
            if i != tags[-1]:
                text += '| '

        await message.answer(f'<i>Вот список всех добавленных на данный момент промокодов:</i>\n\n{text}')
        await Admin_waiting_group.delete_promo.set()

    elif message.text == 'Отмена':
        choose_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        choose_chapter_keyboard.add('Список промокодов')
        choose_chapter_keyboard.add('Добавить промокод')
        choose_chapter_keyboard.add('Удалить промокод')
        choose_chapter_keyboard.add('Назад')

        await message.answer('Выберите действие', reply_markup=choose_chapter_keyboard)
        await Admin_waiting_group.tags_promos.set()

    else:
        tags = []
        sql.execute('''SELECT tag FROM tags''')
        for i in sql.fetchall():
            tags.append(i[0])

        if message.text not in tags:
            await message.answer('Вы неправильно указали название промокода, либо такого тэга не существует')
            return

        sql.execute(f'''DELETE FROM tags WHERE tag = "{message.text}"''')
        database.commit()

        choose_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        choose_chapter_keyboard.add('Список промокодов')
        choose_chapter_keyboard.add('Добавить промокод')
        choose_chapter_keyboard.add('Удалить промокод')
        choose_chapter_keyboard.add('Назад')

        await message.answer('Промокод был успешно удален', reply_markup=choose_chapter_keyboard)
        await Admin_waiting_group.tags_promos.set()



# НАСТРОЙКА ТЭГОВ И ПРОМОКОДОВ
#
#


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(Admin_menu, state='*', commands='admin')

    # Рассылки
    dp.register_message_handler(variants, state=Admin_waiting_group.admin_menu_waiting)
    dp.register_message_handler(mailing_settings, state=Admin_waiting_group.choose_mailing_variant)
    dp.register_message_handler(id_mailing_settings, state=Admin_waiting_group.id_mailing_settings, content_types=['text', 'document'])
    dp.register_message_handler(mailing_tag_settings, state=Admin_waiting_group.tags_mailing_settings)
    dp.register_message_handler(default_mailing, state=Admin_waiting_group.default_mailing_waiting_text, content_types=['text', 'photo'])
    dp.register_message_handler(default_mailing_settings, state=Admin_waiting_group.default_mailing_waiting_next_action)
    dp.register_message_handler(default_mailing_add_link_button, state=Admin_waiting_group.default_mailing_waiting_link_button_setting)
    dp.register_message_handler(default_mailing_add_message_chain, state=Admin_waiting_group.default_mailing_waiting_message_chain_setting, content_types=['text', 'photo'])
    dp.register_message_handler(default_mailing_confirm, state=Admin_waiting_group.default_mailing_waiting_confirm_sending)
    # Рассылки

    # Вопросы
    dp.register_message_handler(delete_question_confirm, state=Admin_waiting_group.delete_question_confirm)
    dp.register_message_handler(edit_question_number_confirm, state=Admin_waiting_group.edit_number_question_confirm)
    dp.register_message_handler(edit_question_number, state=Admin_waiting_group.edit_number_question)
    dp.register_message_handler(edit_question_title_confirm, state=Admin_waiting_group.edit_question_edit_name_confirm)
    dp.register_message_handler(edit_question_title, state=Admin_waiting_group.edit_question_edit_name)
    dp.register_message_handler(edit_questions_choose_subgroup, state=Admin_waiting_group.waiting_choose_question)
    dp.register_message_handler(edit_question, state=Admin_waiting_group.edit_question)
    dp.register_message_handler(new_question_confirm, state=Admin_waiting_group.new_question_confirm)
    dp.register_message_handler(new_question_add_subgroups, state=Admin_waiting_group.new_question_wait_text_description)
    dp.register_message_handler(wait_quantity_subgroups, state=Admin_waiting_group.new_question_wait_number)
    dp.register_message_handler(new_question, state=Admin_waiting_group.new_question)
    dp.register_message_handler(delete_question, state=Admin_waiting_group.delete_question)
    dp.register_message_handler(questions_settings, state=Admin_waiting_group.choose_questions_settings)
    # Вопросы

    # Подразделы
    dp.register_message_handler(edit_subgroup_text_confirm, state=Admin_waiting_group.edit_subgroup_text_confirm)
    dp.register_message_handler(edit_subgroup_text, state=Admin_waiting_group.edit_subgroup_text)
    dp.register_message_handler(edit_subgroup_title_confirm, state=Admin_waiting_group.edit_subgroup_title_confirm)
    dp.register_message_handler(edit_subgroup_title, state=Admin_waiting_group.edit_subgroup_title)
    dp.register_message_handler(delete_subgroup_confirm, state=Admin_waiting_group.delete_subgroup_confirm)
    dp.register_message_handler(delete_subgroup, state=Admin_waiting_group.delete_subgroup)
    dp.register_message_handler(new_subgroup_confirm, state=Admin_waiting_group.new_subgroup_confirm)
    dp.register_message_handler(new_subgroup, state=Admin_waiting_group.new_subgroup)
    dp.register_message_handler(edit_subgroups, state=Admin_waiting_group.edit_question_edit_subgroups)
    # Подразделы

    # Приветственное сообщение
    dp.register_message_handler(new_start_message, state=Admin_waiting_group.new_start_message)
    dp.register_message_handler(new_start_message_confirm, state=Admin_waiting_group.new_start_message_confirm)
    # Приветственное сообщение

    # Тэги и промокоды
    dp.register_message_handler(promos_settings, state=Admin_waiting_group.tags_promos)
    dp.register_message_handler(new_promo, state=Admin_waiting_group.new_promo)
    dp.register_message_handler(delete_promo, state=Admin_waiting_group.delete_promo)
    # Тэги и промокоды



