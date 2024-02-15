from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery

from project.bot.handlers.private.windows import Window
from project.bot.manager import Manager
from project.bot.utils.states import State
from project.bot.utils.texts.buttons import ButtonCode
from project.db.models import ChatDB

router = Router()
router.callback_query.filter(F.message.chat.type == "private")


@router.callback_query(F.data == ButtonCode.MAIN)
async def main_callback_query(call: CallbackQuery, manager: Manager) -> None:
    await Window.main_menu(manager)
    await call.answer()


@router.callback_query(State.MAIN_MENU)
async def main_menu_callback_query(call: CallbackQuery, manager: Manager) -> None:
    if call.data == ButtonCode.ISSUES_LIST:
        await Window.issues_list(manager)

    elif call.data in [ButtonCode.SUBSCRIBE_NOTIFICATION, ButtonCode.UNSUBSCRIBE_NOTIFICATION]:
        broadcast = True if call.data == ButtonCode.SUBSCRIBE_NOTIFICATION else False
        await ChatDB.create_or_update(
            manager.sessionmaker,
            id=manager.user_db.id,
            broadcast=broadcast,
            type=ChatType.PRIVATE,
            title=manager.user_db.full_name,
            username=manager.user_db.username,
        )
        await Window.main_menu(manager)

    await call.answer()


@router.callback_query(State.ISSUES_LIST)
async def issues_list_callback_query(call: CallbackQuery, manager: Manager) -> None:
    if call.data == ButtonCode.BACK:
        await manager.state.update_data(page=1)
        await Window.main_menu(manager)
    elif call.data.isdigit():
        issue_number = int(call.data)
        await manager.state.update_data(issue_number=issue_number)
        await Window.issue_info(manager)
    elif call.data.startswith("page"):
        state_data = await manager.state.get_data()
        current_page = state_data.get("page", 1)
        page = int(call.data.split(":")[1])
        if current_page != page:
            await manager.state.update_data(page=page)
            await Window.issues_list(manager)

    await call.answer()


@router.callback_query(State.ISSUE_INFO)
async def issue_info_callback_query(call: CallbackQuery, manager: Manager) -> None:
    if call.data == ButtonCode.BACK:
        await Window.issues_list(manager)

    await call.answer()
