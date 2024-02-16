from typing import Union, Tuple, List

from aiogram.utils.markdown import hlink
from project.db.models import IssueDB
from project.github.models import Issue
from project.society.models import User


def get_github_link(login: str) -> str:
    return f"<a href='https://github.com/{login}'>{login}</a>"


def format_issue_notify_to_message(text: str, issue: Union[Issue, IssueDB]) -> str:
    format_data = {
        "number": f"<b>#{issue.number}</b>"
        if issue.number else "",

        "url": f"<a href='{issue.url}'>Link</a>"
        if issue.url else "",

        "title": f"<b>{issue.title}</b>"
        if issue.title else "",

        "creator": f"<b>Creator:</b> {get_github_link(issue.creator)}"
        if issue.creator else "",

        "summary": f"<b>Summary:</b>\n<blockquote>{issue.summary}</blockquote>"
        if issue.summary and len(issue.summary) <= 2048
        else f"<blockquote>{issue.summary[:2048]}...</blockquote>"
        if issue.summary else "",

        "rewards": f"<b>Rewards:</b>\n{issue.rewards}"
        if issue.rewards else "",

        "labels": " ".join([f"🏷 <code>{label}</code>" for label in issue.labels])
        if issue.labels else "",

        "assignee": f"<b>Assignee:</b> {get_github_link(issue.assignee)}"
        if issue.assignee else "",

        "assignees": f"<b>Assignees:</b> {', '.join([get_github_link(assignee) for assignee in issue.assignees])}"
        if issue.assignees else "",

        "state": f"<b>State:</b> {issue.state}"
        if issue.state else "",

        "state_reason": f"<b>State reason:</b> {issue.state_reason}"
        if issue.state_reason else "",

        "created_at": f"<b>Created at:</b> {issue.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        if issue.created_at else "",

        "updated_at": f"<b>Updated at:</b> {issue.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        if issue.updated_at else "",

        "closed_at": f"<b>Closed at:</b> {issue.closed_at.strftime('%Y-%m-%d %H:%M:%S')}"
        if issue.closed_at else "",
    }

    return text.format_map(format_data)


def format_weekly_notify_to_message(text: str, stats: Tuple[int, int, int]) -> str:
    format_data = {
        "num_active": stats[0],
        "num_approved_assignee": stats[1],
        "num_suggested_opinions": stats[2],
    }

    return text.format_map(format_data)


def format_top_contributors(text: str, stats: List[User]) -> str:
    format_data = {
        "top_contributors": "<br>".join(
            [
                f"{i}. {hlink(user.name, user.society_url)}"
                f"- <b>{user.awards_count}</b>"
                for i, user in enumerate(stats, start=1)
            ]
        )
    }
    return text.format_map(format_data)
