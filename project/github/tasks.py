import asyncio
from typing import List, Tuple, Any

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup as Markup
from sqlalchemy.ext.asyncio import async_sessionmaker

from .api import GitHubAPI
from .models import Issue
from ..bot.utils.texts.buttons import TextButton, ButtonCode
from ..bot.utils.texts.messages import TextMessage, MessageCode
from ..config import BOUNTIES_CREATOR_BOT_URL
from ..db.models import IssueDB, ChatDB


async def track_and_notify_issue() -> None:
    loop = asyncio.get_event_loop()
    bot: Bot = loop.__getattribute__("bot")
    githubapi: GitHubAPI = loop.__getattribute__("githubapi")
    sessionmaker: async_sessionmaker = loop.__getattribute__("sessionmaker")

    issue_db: List[IssueDB] = await IssueDB.get_all(sessionmaker)
    issues_github: List[Issue] = await githubapi.get_issues_all("all")
    created_issues, closing_issues, approved_issues, completed_issues = await _categorize(issue_db, issues_github)

    if not created_issues and not closing_issues and not completed_issues: return  # noqa:E701

    chats: List[ChatDB] = await ChatDB.get_all(sessionmaker)
    create_bounty_button = await TextButton(sessionmaker).get_button(
        ButtonCode.CREATE_BOUNTY, url=BOUNTIES_CREATOR_BOT_URL
    )

    async def send_message(text: str, reply_markup: Markup) -> None:
        for chat in chats:
            await bot.send_message(chat.id, text=text, reply_markup=reply_markup)
            await asyncio.sleep(0.05)

    async def notify_issue(issue_list: List[Issue], message_code: str, button_code: str) -> None:
        message_text = await TextMessage(sessionmaker).get(message_code)
        button_text = await TextButton(sessionmaker).get_button(button_code)
        for issue in issue_list:
            text = message_text.format_map(issue.model_dump())
            reply_markup = Markup(inline_keyboard=[[button_text], [create_bounty_button]])
            await send_message(text, reply_markup)

    if created_issues:
        await notify_issue(created_issues, MessageCode.ISSUE_CREATED, ButtonCode.ISSUE_CREATED)

    if closing_issues:
        await notify_issue(closing_issues, MessageCode.ISSUE_CLOSING, ButtonCode.ISSUE_CLOSING)

    if approved_issues:
        await notify_issue(approved_issues, MessageCode.ISSUE_APPROVED, ButtonCode.ISSUE_APPROVED)

    if completed_issues:
        await notify_issue(completed_issues, MessageCode.ISSUE_COMPLETED, ButtonCode.ISSUE_COMPLETED)

    await IssueDB.update_all(sessionmaker, issues_github)


async def _categorize(
        issue_db: List[IssueDB],
        issues_github: List[Issue],
) -> Tuple[list[Issue], list[Any], list[Any], list[Any]]:
    approved_issues, completed_issues, closing_issues = [], [], []
    issue_db_numbers = {i.number for i in issue_db}
    created_issues = [i for i in issues_github if i.number not in issue_db_numbers]

    for issue, issue_db in zip(
            sorted(issues_github, key=lambda x: x.number),
            sorted(issue_db, key=lambda x: x.number),
    ):
        if issue in created_issues:
            continue
        if (
                "Approved" in issue.labels
                and "Approved" not in issue_db.labels
                and issue.assignee is None
                and issue_db.assignee is None
        ):
            approved_issues.append(issue)
        elif (
                issue.state == "closed"
                and issue_db.state != "closed"
                and issue.state_reason == "completed"
                and issue_db.state_reason != "completed"
        ):
            completed_issues.append(issue)
        elif (
                "Closing Soon as Not planning" in issue.labels
                and "Closing Soon as Not planning" not in issue_db.labels
        ):
            closing_issues.append(issue)

    return created_issues, closing_issues, approved_issues, completed_issues
