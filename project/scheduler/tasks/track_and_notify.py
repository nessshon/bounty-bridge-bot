import asyncio
from typing import List, Tuple, Any

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup as Markup
from aiogram.types import InlineKeyboardButton as Button
from sqlalchemy.ext.asyncio import async_sessionmaker

from ...apis.github import GitHubAPI
from ...apis.github.models import Issue
from ...bot.utils.formatters import format_issue_notify_to_message
from ...bot.utils.messages import send_message
from ...bot.utils.texts.buttons import TextButton, ButtonCode
from ...bot.utils.texts.messages import TextMessage, MessageCode
from ...config import BOUNTIES_CREATOR_BOT_URL
from ...db.models import IssueDB, ChatDB


async def track_and_notify() -> None:
    """
    Track and notify about GitHub issues.
    """
    loop = asyncio.get_event_loop()
    bot: Bot = loop.__getattribute__("bot")
    githubapi: GitHubAPI = loop.__getattribute__("githubapi")
    sessionmaker: async_sessionmaker = loop.__getattribute__("sessionmaker")

    # Fetch issues from the database and GitHub
    issue_db: List[IssueDB] = await IssueDB.get_all(sessionmaker)
    issues_github: List[Issue] = await githubapi.get_issues_all("all")

    # Categorize issues into different lists
    created_issues, closing_issues, approved_issues, completed_issues = await _categorize(issue_db, issues_github)

    # Update the database with the latest GitHub issues
    await IssueDB.update_all(sessionmaker, issues_github)

    # If no issues to notify, return
    if not any([created_issues, closing_issues, approved_issues, completed_issues]):
        return None

    # Retrieve all chats ids
    chats_ids: List[int, None] = await ChatDB.get_all_ids(sessionmaker)
    create_bounty_button = await TextButton(sessionmaker).get_button(
        ButtonCode.CREATE_BOUNTY, url=BOUNTIES_CREATOR_BOT_URL
    )

    async def notify(issue_list: List[Issue], message_code: str, button_code: str) -> None:
        # Notify users about issues
        message_text = await TextMessage(sessionmaker).get(message_code)
        button_text = await TextButton(sessionmaker).get(button_code)

        for issue in issue_list:
            text = format_issue_notify_to_message(message_text, issue)
            button = Button(text=button_text, url=issue.url)
            reply_markup = Markup(inline_keyboard=[[button], [create_bounty_button]])

            for chat_id in chats_ids:
                await send_message(bot, chat_id, text, reply_markup=reply_markup)

    # Notify about different types of issues
    if created_issues:
        await notify(created_issues, MessageCode.ISSUE_CREATED, ButtonCode.ISSUE_CREATED)

    if closing_issues:
        await notify(closing_issues, MessageCode.ISSUE_CLOSING, ButtonCode.ISSUE_CLOSING)

    if approved_issues:
        await notify(approved_issues, MessageCode.ISSUE_APPROVED, ButtonCode.ISSUE_APPROVED)

    if completed_issues:
        await notify(completed_issues, MessageCode.ISSUE_COMPLETED, ButtonCode.ISSUE_COMPLETED)


async def _categorize(
        issue_db: List[IssueDB],
        issues_github: List[Issue],
) -> Tuple[List[Issue], List[Any], List[Any], List[Any]]:
    """
    Categorize GitHub issues into different lists based on their status.

    :param issue_db: List of issues from the database.
    :param issues_github: List of issues from the GitHub API.
    :return: Tuple containing lists of created, closing, approved, and completed issues.
    """
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
