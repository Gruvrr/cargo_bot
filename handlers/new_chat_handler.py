from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, Bot
from services.chat_service import Chat


router = Router()


@router.callback_query(lambda c: c.data == "call_manager")
async def call_manager(callback: CallbackQuery, bot: Bot):
    try:
        user_id = callback.from_user.id
        username = callback.from_user.username or None
        manager_telegram_id = Chat.new_callback_from_user(user_id, username)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Ответить", callback_data=f"start_chat:{user_id}")]
            ]
        )
        await callback.message.answer(text="Менеджер получил ваше уведомление. Как только он освободится, он сразу свяжется с вами.")
        await bot.send_message(manager_telegram_id, text=f"Вас вызывается пользователь @{username}", reply_markup=keyboard)
    except Exception as _ex:
        print(f"[ERROR CALL MANAGER] - {_ex}")


@router.callback_query(lambda c: c.data.startswith("start_chat:"))
async def start_chat_with_user(callback: CallbackQuery, bot: Bot):
    try:
        manager_id = callback.from_user.id
        user_id = callback.data.split(':')[1]
        if Chat.new_chat_with_user(user_id, manager_id):

            await bot.send_message(manager_id, text=f"Вы начали диалог с пользователем {user_id}")
    except Exception as _ex:
        print(f"[ERROR start_chat] {_ex}")





