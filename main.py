import asyncio
from aiogram.filters import Command
from aiogram.types import Message
from handlers import (new_waybill_handler, new_clime_handler, end_chat_handler, manager_chat_handler,
                      user_chat_handler, new_chat_handler, handler, get_all_claims_handler)
from services.user_service import UserService
from services.user_state_service import notify_unfinished_tasks
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv
from keyboards.inline import start_keyboard
from apscheduler.schedulers.asyncio import AsyncIOScheduler


load_dotenv()
dp = Dispatcher()
token = getenv("TOKEN")
manager_id = getenv("ADMIN_ID")
admin_id = getenv("ADMIN_ID")


async def start_bot(bot: Bot):
    await bot.send_message(admin_id, text="Bot is start")


async def stop_bot(bot: Bot):
    await bot.send_message(admin_id, text="Бот остановлен")


async def hello_msg(message: Message):
    if UserService.is_user_manager(message.from_user.id):
        await message.answer(text=f"Привет {message.from_user.first_name}. Рад видеть тебя на смене."
                                  f"Ниже ты можешь выбрать действия для менеджера.")
        await handler.send_menu(message)
    else:
        user_data = {
            'user_id': message.from_user.id,
            'telegram_user_id': message.from_user.id,
            'username': message.from_user.username,
            'is_manager': False,
            'manager_id': 2
        }
        UserService.create_new_user(user_data)

        await message.answer(text="Выберите действие ⬇️⬇️⬇️", reply_markup=start_keyboard)


async def notify_unfinished_tasks_wrapper(bot):
    await notify_unfinished_tasks(bot)


async def start():

    bot = Bot(token=token, parse_mode='HTML')

    dp.include_routers(new_waybill_handler.router, new_clime_handler.router, new_chat_handler.router,
                       end_chat_handler.router, manager_chat_handler.router, user_chat_handler.router, handler.router,
                       get_all_claims_handler.router)
    dp.message.register(hello_msg, Command('start'))
    dp.message.register(handler.send_menu, Command('menu'))
    dp.message.register(get_all_claims_handler.get_all_claims, Command('get_all_claims'))
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_unfinished_tasks, args=[bot], trigger='interval', minutes=60)
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())