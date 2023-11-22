from aiogram import Router, Bot
from aiogram.types import Message
from utils.database import connect,close
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()


def is_client(user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s AND ismanager = False", (user_id,))
        user_db_id = cursor.fetchone()
        if user_db_id is None:
            return False

        user_db_id = user_db_id[0]

        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM chats WHERE userid = %s LIMIT 1
            )
        """, (user_db_id,))
        has_active_chat = cursor.fetchone()[0]
        return has_active_chat
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        close(conn)


async def is_client_filter(message: Message) -> bool:
    return is_client(message.from_user.id)


@router.message(is_client_filter)
async def forward_message_from_client_to_manager(message: Message, bot: Bot):
    user_id = message.from_user.id
    new_message = message.text
    conn = connect()
    cursor = conn.cursor()
    end_chat_button = KeyboardButton(text='/end_chat')
    end_chat_keyboard = ReplyKeyboardMarkup(keyboard=[[end_chat_button]], resize_keyboard=True)
    try:
        cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s AND ismanager = False", (user_id,))
        user_db_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT chatid, managerid
            FROM chats
            WHERE userid = %s
            LIMIT 1
        """, (user_db_id,))
        chat_info = cursor.fetchone()
        if chat_info:
            chat_id, manager_id = chat_info

            cursor.execute("""
                UPDATE chats
                SET messages = messages || %s
                WHERE chatid = %s
            """, (new_message, chat_id))
            conn.commit()

            cursor.execute("SELECT telegramuserid FROM managers WHERE managerid = %s", (manager_id,))
            manager_telegram_id = cursor.fetchone()[0]
            if manager_telegram_id:
                await bot.send_message(manager_telegram_id, new_message, reply_markup=end_chat_keyboard)
        else:
            await message.reply("Активный чат не найден.")
    except Exception as _ex:
        print(f"[ERROR] {_ex}")
    finally:
        close(conn)
