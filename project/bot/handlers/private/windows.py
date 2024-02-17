from project.bot.manager import Manager
from project.bot.utils import keyboards
from project.bot.utils.formatters import format_issue_notify_to_message, format_top_contributors_to_message
from project.bot.utils.states import State
from project.bot.utils.texts.messages import MessageCode
from project.db.models import IssueDB
from project.apis.society.storage import SocietyStorage


class Window:

    @staticmethod
    async def main_menu(manager: Manager) -> None:
        text = await manager.text_message.get(MessageCode.MAIN_MENU)
        reply_markup = await keyboards.main_menu(manager.text_button, manager.user_db.broadcast)

        await manager.send_message(text, reply_markup=reply_markup)
        await manager.state.set_state(State.MAIN_MENU)

    @classmethod
    async def issues_list(cls, manager: Manager) -> None:
        state_data = await manager.state.get_data()
        page, page_size = state_data.get("page", 1), 7

        db_items = await IssueDB.paginate(
            manager.sessionmaker,
            page_number=page,
            page_size=page_size,
            order_by=IssueDB.number.desc(),
        )
        items = [(f"{i.title[:50]}..." if len(i.title) > 50 else i.title, i.number) for i in db_items]
        total_pages = await IssueDB.total_pages(
            manager.sessionmaker,
            page_size=page_size,
        )
        text = await manager.text_message.get(MessageCode.ISSUES_LIST)
        reply_markup = await keyboards.issues_list(manager.text_button, items, page, total_pages)

        await manager.send_message(text, reply_markup=reply_markup)
        await manager.state.set_state(State.ISSUES_LIST)

    @staticmethod
    async def issue_info(manager: Manager) -> None:
        state_data = await manager.state.get_data()
        issue_number = state_data.get("issue_number")
        issue = await IssueDB.get(manager.sessionmaker, issue_number)

        text = await manager.text_message.get(MessageCode.ISSUE_INFO)
        text = format_issue_notify_to_message(text, issue)
        reply_markup = await keyboards.issue_info(manager.text_button, issue.url)

        await manager.send_message(text, reply_markup=reply_markup)
        await manager.state.set_state(State.ISSUE_INFO)

    @staticmethod
    async def top_contributors(manager: Manager) -> None:
        society_storage = SocietyStorage()
        stats = await society_storage.get_top()

        text = await manager.text_message.get(MessageCode.TOP_CONTRIBUTORS)
        text = format_top_contributors_to_message(text, stats)
        reply_markup = await keyboards.top_contributors(manager.text_button)

        await manager.send_message(text, reply_markup=reply_markup)
        await manager.state.set_state(State.TOP_CONTRIBUTORS)
