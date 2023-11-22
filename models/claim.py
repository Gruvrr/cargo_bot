from aiogram.fsm.state import StatesGroup, State


class Claim_state(StatesGroup):
    waybillid = State()
    email = State()
    description = State()
    amountrequested = State()
    evidence = State()


class Claim:
    def __init__(self, waybillid, userid, email, description, amountrequested, evidence):
        self.waybillid = waybillid
        self.userid = userid
        self.email = email
        self.description = description
        self.amountrequested = amountrequested
        self.evidence = evidence