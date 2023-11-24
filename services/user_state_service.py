from aiogram import Bot
from utils.database import connect, close
from os import getenv
from dotenv import load_dotenv

load_dotenv()
manager_id = getenv("MANAGER_ID")


async def log_start_task(telegram_user_id: int, state: str):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (telegram_user_id,))
        user_db_id = cursor.fetchone()
        if not user_db_id:
            print(f"Пользователь с Telegram ID {telegram_user_id} не найден в таблице users")
            return
        user_db_id = user_db_id[0]

        cursor.execute("""
            INSERT INTO user_states (userid, state)
            VALUES (%s, %s)
        """, (user_db_id, state))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при записи начала задачи: {e}")
    finally:
        close(conn)


async def log_end_task(telegram_user_id: int, state: str):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Получение userid из таблицы users
        cursor.execute("SELECT userid FROM users WHERE telegramuserid = %s", (telegram_user_id,))
        user_db_id = cursor.fetchone()
        if not user_db_id:
            print(f"Пользователь с Telegram ID {telegram_user_id} не найден в таблице users")
            return
        user_db_id = user_db_id[0]

        # Находим последнюю запись состояния для обновления
        cursor.execute("""
            SELECT state_id FROM user_states
            WHERE userid = %s AND state = %s AND end_time IS NULL
            ORDER BY start_time DESC
            LIMIT 1
        """, (user_db_id, state))
        state_record = cursor.fetchone()
        if state_record:
            state_id = state_record[0]

            # Обновление времени завершения для найденной записи
            cursor.execute("""
                UPDATE user_states
                SET end_time = CURRENT_TIMESTAMP
                WHERE state_id = %s
            """, (state_id,))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при записи завершения задачи: {e}")
    finally:
        close(conn)


async def notify_unfinished_tasks(bot: Bot):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.telegramuserid, u.username, us.state
            FROM user_states us
            JOIN users u ON us.userid = u.userid
            WHERE us.end_time IS NULL
        """)
        unfinished_tasks = cursor.fetchall()

        for telegram_id, username, state in unfinished_tasks:
            manager_telegram_id = manager_id
            message = f"Пользователь @{username} с ID {telegram_id} не завершил задачу: {state}"
            await bot.send_message(manager_telegram_id, message)
    except Exception as e:
        print(f"Ошибка при проверке незавершенных задач: {e}")
    finally:
        close(conn)
