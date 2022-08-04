import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

# from BOT.app.Classes.States_classes import TOKEN
from Kwork_order_bot.App.Admin_callbacks.Admin_callbacks import register_callbacks
from Kwork_order_bot.App.All_admin_handlers.Admin_menu_handlers import register_admin_menu_handlers
from Kwork_order_bot.App.All_user_handlers.Main_menu_handlers import register_main_menu_handlers
from Kwork_order_bot.App.All_user_handlers.Start_handlers import register_handlers_start
from Kwork_order_bot.App.All_user_handlers.User_handlers import register_user_handlers
from Kwork_order_bot.settings import TOKEN

logger = logging.getLogger(__name__)

# БАЗА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ

database = sqlite3.connect('database.db')
sql = database.cursor()
sql.execute('''
            CREATE TABLE IF NOT EXISTS user_database
                (id INTEGER,
                 mailing STRING)
            ''')
database.commit()

# sql.execute('''
#             CREATE TABLE IF NOT EXISTS promocodes
#                 (id INTEGER,
#                  promocode STRING,
#                  tag TEXT)
#             ''')
# database.commit()

sql.execute('''
            CREATE TABLE IF NOT EXISTS tags
                (id INTEGER,
                 tag STRING,
                 users TEXT)
            ''')
database.commit()

admin_database = sqlite3.connect('admin_database.db')
sql_admin = admin_database.cursor()

sql_admin.execute('''
            CREATE TABLE IF NOT EXISTS main_menu_message
                (id INTEGER,
                text TEXT)
            ''')
admin_database.commit()

sql_admin.execute('''SELECT * FROM main_menu_message''')
if len(sql_admin.fetchall()) == 0:
    default = (1, 'Здравствуйте! Чем можем помочь? Выберите вариант или просто напишите нам свой вопрос!\n\n'
        'У нас новая страница в инстаграме: ivolgaactiv_\n'
        '*Meta Platforms Inc. признана экстремистской организацией на территории РФ\n\n'
        'Так же вы можете позвонить на бесплатную горячую линию: 8 800 250-41-29')

    sql_admin.execute('''
                      INSERT INTO main_menu_message VALUES (?,?)
                      ''', default)
    admin_database.commit()

    print('Приветственное сообщение установлено')

sql_admin.execute('''
            CREATE TABLE IF NOT EXISTS questions
                (id INTEGER,
                title STRING,
                subgroups TEXT)
            ''')
admin_database.commit()




# ОСНОВНЫЕ ОБРАБОТЧИКИ

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить/перезапустить бота")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Объявление и инициализация объектов бота и диспетчера
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров Админа

    register_admin_menu_handlers(dp)

    # Регистрация хэндлеров

    register_handlers_start(dp)
    register_main_menu_handlers(dp)

    register_user_handlers(dp)

    # Регистрация колбэков

    register_callbacks(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
