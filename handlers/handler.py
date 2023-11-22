from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from os import getenv
from dotenv import load_dotenv

load_dotenv()
router = Router()
manager_id = getenv("MANAGER_ID")


async def send_menu(message: Message):
    if str(message.from_user.id) == manager_id:
        buttons = [
            [KeyboardButton(text=command) for command in ["/get_all_claims", "/end_chat"]],
        ]
        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("Выберите команду:", reply_markup=markup)
    else:
        await message.answer("У вас нет доступа к этому меню.")