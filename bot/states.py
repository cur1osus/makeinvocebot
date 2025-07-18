from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    enter_question = State()
