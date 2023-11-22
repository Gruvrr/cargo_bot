import os
import re
from utils.database import connect, close
from aiogram.types import Message, CallbackQuery
from aiogram import Router, Bot
from models.claim import Claim_state, Claim
from services.claim_service import ClaimService
from aiogram.fsm.context import FSMContext
from services.user_state_service import log_start_task, log_end_task

email_regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
router = Router()


def check_waybill_exists(waybill_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM waybills WHERE waybillid = %s", (waybill_id,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке наличия накладной: {e}")
        return False
    finally:
        close(conn)


@router.callback_query(lambda c: c.data == "register_claim")
async def make_new_clime(callback: CallbackQuery, state: FSMContext):
    await log_start_task(callback.from_user.id, "make_waybill")
    await state.set_state(Claim_state.waybillid)
    await callback.message.answer(text="Введите номер накладной")


@router.message(Claim_state.waybillid)
async def sey_email(message: Message, state: FSMContext):
    waybill_id = message.text
    if not waybill_id.isdigit():
        await message.reply("Пожалуйста, введите номер накладной.")
        return

    if not check_waybill_exists(waybill_id):
        await message.reply("Такого номера накладной не существует. Пожалуйста, введите корректный номер.")
        return

    await state.update_data(waybillid=waybill_id)
    await state.set_state(Claim_state.email)
    await message.answer(text="Введите email для ответа")


@router.message(Claim_state.email)
async def say_description(message: Message, state: FSMContext):
    if not email_regex.match(message.text):
        await message.reply("Пожалуйста, введите корректный адрес электронной почты.")
        return
    await state.update_data(email=message.text)
    await state.set_state(Claim_state.description)
    await message.answer(text="Опишите вашу проблему")


@router.message(Claim_state.description)
async def say_amountrequested(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Claim_state.amountrequested)
    await message.answer(text="Введите требуемую сумму")


@router.message(Claim_state.amountrequested)
async def say_avidance(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите число.")
        return
    await state.update_data(amount_requested=message.text)
    await state.set_state(Claim_state.evidence)
    await message.answer(text="Пришлите фото или скан документов")


@router.message(Claim_state.evidence)
async def res(message: Message, state: FSMContext, bot: Bot):
    try:
        media = message.photo[-1] if message.photo else message.document

        if message.document and not message.document.file_name.endswith('.jpg'):
            await message.answer("Пожалуйста, отправьте файл в формате .jpg.")
            return

        user_id = message.from_user.id
        user_dir = f"user_{user_id}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        file_id = media.file_id
        file_name = file_id + ".jpg"
        file_path = os.path.join(user_dir, file_name)

        file = await bot.get_file(file_id)
        await bot.download_file(file_path=file.file_path, destination=file_path)
        data = await state.get_data()
        user_id = ClaimService.get_user_id(message.from_user.id)
        manager_id = ClaimService.get_manager_id(message.from_user.id)
        new_clime = Claim(
            waybillid=data.get('waybillid'),
            userid = user_id,
            email=data.get('email'),
            description=data.get('description'),
            amountrequested=data.get('amount_requested'),
            evidence=file_path
        )
        await state.update_data(evidence=file_path)
        ClaimService.create_claim(waybillid=new_clime.waybillid, userid=new_clime.userid, email=new_clime.email,
                                        description=new_clime.description, amount_requested=new_clime.amountrequested,
                                        evidence=new_clime.evidence)
        await bot.send_message(chat_id=manager_id, text=f"Новая претензия от пользователя {message.from_user.username}\n"
                                                        f"Номер накладной - {new_clime.waybillid}\n"
                                                        f"Требуемая сумма - {new_clime.amountrequested}\n"
                                                        f"Описание проблемы - {new_clime.description}\n"
                                                        f"Почта для связи - {new_clime.email}")
        await log_end_task(message.from_user.id, "make_waybill")
        await message.answer(text="Ваша претензия зарегистрирована")
    except Exception as _er:
        print(f"[ERROR] - {_er}")
    finally:
        print(f"ALL GOOD")




