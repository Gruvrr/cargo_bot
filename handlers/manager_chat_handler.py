from aiogram import Router, Bot
from aiogram.types import Message
from utils.database import connect,close
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


def is_manager(telegram_user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM managers WHERE telegramuserid = %s", (telegram_user_id,))
        return cursor.fetchone()[0] > 0
    except Exception as _ex:
        print(f"Database error: {_ex}")
        return False


async def is_manager_filter(message: Message) -> bool:
    return is_manager(message.from_user.id)


@router.message(is_manager_filter)
async def forward_message_from_manager_to_client(message: Message, bot: Bot):
    manager_id = message.from_user.id
    new_message = message.text
    conn = connect()
    cursor = conn.cursor()
    end_chat_button = KeyboardButton(text='/end_chat')
    end_chat_keyboard = ReplyKeyboardMarkup(keyboard=[[end_chat_button]], resize_keyboard=True)
    try:
        cursor.execute("SELECT managerid FROM managers WHERE telegramuserid = %s", (manager_id,))
        manager_db_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT chatid, userid
            FROM chats
            WHERE managerid = %s
            LIMIT 1
        """, (manager_db_id,))
        chat_info = cursor.fetchone()
        if chat_info:
            chat_id, user_id = chat_info

            cursor.execute("""
                UPDATE chats
                SET messages = messages || %s
                WHERE chatid = %s
            """, (new_message, chat_id))
            conn.commit()
            cursor.execute("SELECT telegramuserid FROM users WHERE userid = %s", (user_id,))
            client_telegram_id = cursor.fetchone()[0]
            if client_telegram_id:
                await bot.send_message(client_telegram_id, new_message, reply_markup=end_chat_keyboard)
        else:
            await message.reply("Активный чат не найден.")
    except Exception as _ex:
        print(f"[ERROR] {_ex}")
    finally:
        close(conn)

