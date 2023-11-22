from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, Bot
from aiogram.filters import Command
from utils.database import connect,close
from aiogram.types import Message

router = Router()


async def get_all_claims(message: Message):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT managerid FROM managers WHERE telegramuserid = %s", (message.from_user.id,))
        manager_id = cursor.fetchall()[0]
        cursor.execute("SELECT userid FROM users WHERE managerid = %s", (manager_id,))
        user_rows = cursor.fetchall()

        user_ids = [row[0] for row in user_rows]

        if user_ids:
            query_claims = """
            SELECT claimid, waybillid, userid, email, description, amountrequested, evidence
            FROM claims
            WHERE userid IN %s
            """
            cursor.execute(query_claims, (tuple(user_ids),))
            claim_rows = cursor.fetchall()

            if claim_rows:
                claims_list = []
                for row in claim_rows:
                    claim_info = f"Claim ID: {row[0]}\nWaybill ID: {row[1]}\nUser ID: {row[2]}\nEmail: {row[3]}\nDescription: {row[4]}\nAmount Requested: {row[5]}\nEvidence: {row[6]}\n"
                    claims_list.append(claim_info)

                await message.answer("Список претензий, закрепленных за вашими пользователями:\n\n" + "\n\n".join(claims_list))
            else:
                await message.answer("У вас нет закрепленных претензий.")

        else:
            await message.answer("У вас нет закрепленных пользователей.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        close(conn)

