from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Создать накладную", callback_data='make_waybill')
    ],
    [
        InlineKeyboardButton(text="Регистрация претензии", callback_data='register_claim')
    ],
    [
        InlineKeyboardButton(text="Позвать менеджера", callback_data='call_manager')
    ]
])