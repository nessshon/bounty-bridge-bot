from aiogram.fsm.state import StatesGroup

from aiogram.fsm.state import State as BaseState


class State(StatesGroup):
    MAIN_MENU = BaseState()
    ISSUES_LIST = BaseState()
    ISSUE_INFO = BaseState()
    TOP_CONTRIBUTORS = BaseState()
