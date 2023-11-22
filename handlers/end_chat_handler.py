from aiogram.types import ReplyKeyboardRemove
from aiogram import Router, Bot
from aiogram.types import Message
from utils.database import connect,close
from aiogram.filters import Command

router = Router()


@router.message(Command('end_chat'))
async def end_chat_command(message: Message, bot: Bot):
    telegram_user_id = message.from_user.id
    conn = connect()
    cursor = conn.cursor()
    try:

        cursor.execute("""
            SELECT u.userid, u.ismanager, m.managerid 
            FROM users u
            LEFT JOIN managers m ON u.telegramuserid = m.telegramuserid
            WHERE u.telegramuserid = %s
        """, (telegram_user_id,))

        result = cursor.fetchone()
        if result:
            user_id, is_manager, manager_id = result

            if is_manager and manager_id is not None:
                # Если пользователь - менеджер и имеет соответствующую запись в таблице managers
                target_id = manager_id
            else:
                # Если пользователь не менеджер или не найден в таблице managers
                target_id = user_id
        cursor.execute("""
            DELETE FROM chats
            WHERE userid = %s OR managerid = %s
        """, (target_id, target_id))

        cursor.execute("""
            UPDATE userstates
            SET state = 'chat_ended'
            WHERE userid = %s
        """, (user_id,))
        conn.commit()

        await message.reply("Чат был завершен.", reply_markup=ReplyKeyboardRemove())
    except Exception as _ex:
        print(f"[ERROR] {_ex}")
        await message.reply("Произошла ошибка при завершении чата.")
    finally:
        close(conn)
