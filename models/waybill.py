from aiogram.fsm.state import StatesGroup, State


class Waybill(StatesGroup):
    cargo_description = State()
    cargo_weight = State()
    cargo_dimensions = State()
    address_from = State()
    address_to = State()
    payment_method = State()