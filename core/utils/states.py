from aiogram.dispatcher.fsm.state import State, StatesGroup


class Steps(StatesGroup):
    GET_SUM = State()
    GET_SUM_OUT = State()
    GET_DETAILS = State()
    GET_BID = State()
    GET_TOKEN = State()
    GET_PERCENT = State()
    GET_YOUKASSA_TOKEN = State()
    GET_PAYMENTS = State()