import os

from aiogram.types import Message, CallbackQuery
from aiogram import Router
from models.waybill import Waybill
from aiogram.fsm.context import FSMContext
from services.waybill_service import WaybillService
from utils.pdf_generator import generate_pdf
from aiogram.types import BufferedInputFile
from services.user_state_service import log_start_task, log_end_task

router = Router()


@router.callback_query(lambda c: c.data == "make_waybill")
async def make_new_waybill(callback: CallbackQuery, state: FSMContext):
    await log_start_task(callback.from_user.id, "make_waybill")
    await state.set_state(Waybill.cargo_description)
    await callback.message.answer(text="Введите описание груза")


@router.message(Waybill.cargo_description)
async def sey_weight(message: Message, state: FSMContext):
    await state.update_data(cargo_description=message.text)
    await state.set_state(Waybill.cargo_weight)
    await message.answer(text="Введите вес груза в кг")


@router.message(Waybill.cargo_weight)
async def say_dimensions(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Пожалуйста, введите число (вес груза в кг).")
        return
    await state.update_data(weight=message.text)
    await state.set_state(Waybill.cargo_dimensions)
    await message.answer(text="Введите габариты груза")


@router.message(Waybill.cargo_dimensions)
async def say_address_from(message: Message, state: FSMContext):
    await state.update_data(dimensions=message.text)
    await state.set_state(Waybill.address_from)
    await message.answer(text="Введите адрес отправки")


@router.message(Waybill.address_from)
async def say_address_to(message: Message, state: FSMContext):
    await state.update_data(address_from=message.text)
    await state.set_state(Waybill.address_to)
    await message.answer(text="Введите адрес получения")


@router.message(Waybill.address_to)
async def say_payments_method(message: Message, state: FSMContext):
    await state.update_data(address_to=message.text)
    await state.set_state(Waybill.payment_method)
    await message.answer(text="Введите способ оплаты")


@router.message(Waybill.payment_method)
async def res(message: Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    data = await state.get_data()

    try:
        waybill_id = WaybillService.create_waybill(message.from_user.id, data)
        data['waybill_id'] = waybill_id
        pdf_file_name = generate_pdf(data)

        document = BufferedInputFile.from_file(path=pdf_file_name)
        await log_end_task(message.from_user.id, "make_waybill")
        await message.answer_document(document=document, caption="Ваша накладная")
        os.remove(pdf_file_name)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    await state.clear()


