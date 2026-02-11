from aiogram.fsm.state import State, StatesGroup


class WizardStates(StatesGroup):
    WAITING_LANGUAGE = State()
    WAITING_NAME = State()
    WAITING_DATE_OF_BIRTH = State()
    WAITING_PLACE_OF_BIRTH = State()
    WAITING_PLACE_OF_LIVING = State()
