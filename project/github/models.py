from __future__ import annotations

import re
from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, field_validator, Field


class Issue(BaseModel):
    """Model representing a GitHub issue."""

    number: int
    """Issue number."""

    url: str = Field(alias="html_url")
    """URL to the GitHub issue."""

    title: str
    """Title of the issue."""

    creator: Union[str, None] = Field(alias="user")
    """GitHub user login or None if not assigned."""

    assignee: Union[str, None]
    """GitHub user login or None if not assigned."""

    assignees: List[Union[str, None]]
    """List of GitHub user logins or None if not assigned."""

    labels: List[Union[str, None]]
    """List of GitHub label names or None if not assigned."""

    rewards: Union[str, None] = Field(default="-", alias="body")
    """Rewards of the issue or None if not assigned."""

    summary: Union[str, None] = Field(default="-", alias="body")
    """Summary of the issue or None if not assigned."""

    state: str
    """State of the issue (e.g. open, closed)."""

    state_reason: Union[str, None] = None
    """Reason for the state of the issue or None if not assigned (e.g. completed, not not_planned)."""

    created_at: datetime
    """Datetime when the issue was created."""

    updated_at: Union[datetime, None]
    """Datetime when the issue was last updated or None if not updated."""

    closed_at: Union[datetime, None]
    """Datetime when the issue was closed or None if not closed."""

    @field_validator("creator", mode="before")
    def extract_user_login(cls, value):  # noqa
        """Extracts GitHub user login from the given value."""
        return value["login"] if value else None

    @field_validator("assignee", mode="before")
    def extract_assignee_login(cls, value):  # noqa
        """Extracts GitHub assignee login from the given value."""
        return value["login"] if value else None

    @field_validator("assignees", mode="before")
    def extract_assignees_login(cls, values):  # noqa
        """Extracts GitHub assignees logins from the given values."""
        return [assignee["login"] if assignee else None for assignee in values]

    @field_validator("labels", mode="before")
    def extract_labels_name(cls, values):  # noqa
        """Extracts GitHub label names from the given values."""
        return [label["name"] if label else None for label in values]

    @field_validator("rewards", mode="before")
    def extract_rewards(cls, value):  # noqa
        """Extracts rewards from the given value (body)."""
        patterns = [
            r'Estimate suggested reward\r\n\r\n(.*?)\r\n\r\n',
            r'Estimate suggested reward\r\n(.*?)\r\n\r\n',
            r'Estimate suggested reward\n\n(.*?)\n\n',
            r'Estimate suggested reward\r\n(.*?$)',
            r'Estimate suggested reward\n\n(.*?$)',
            r'REWARD\r\n\r\n(.*?)\r\n\r\n',
            r'Reward\r\n\r\n(.*?)\r\n\r\n',
            r'Reward\r\n\r\n(.*?$)',
            r'Reward\n\n(.*?)\n\n',
            r'Reward\r\n(.*?$)',
        ]
        if value is not None:
            # Replace "- " and "* " with "• " in the value
            value = value.replace("- ", "• ").replace("* ", "• ")
        return cls._extract_information(patterns, value)

    @field_validator("summary", mode="before")
    def extract_summary(cls, value):  # noqa
        """Extracts summary from the given value (body)."""
        patterns = [
            r'Summary\r\n(.*?)\r\n\r\n',
            r'Summary\n\n(.*?)\n\n',
        ]
        return cls._extract_information(patterns, value)

    @classmethod
    def _extract_information(cls, patterns: List[str], value: Optional[str]) -> Optional[str]:
        """Extracts information from the given value using the given patterns."""
        # Check if the input value is a string
        if not isinstance(value, str):
            return None

        # Iterate through the provided patterns
        for pattern in patterns:
            # Use regular expression to find a match in the value
            match = re.search(pattern, value, re.DOTALL)
            if match:
                # Extract text from the matched group and remove leading/trailing whitespaces
                text = match.group(1).strip()

                # Define a pattern for converting Markdown links to HTML links
                markdown_link_pattern = re.compile(r'\[([^]]+)]\(([^)]+)\)')

                # Define a function to convert Markdown links to HTML links
                def markdown_to_html(m):
                    link_text = m.group(1)
                    link_url = m.group(2)
                    return f'<a href="{link_url}">{link_text}</a>'

                # Apply the Markdown to HTML conversion to the extracted text
                return re.sub(markdown_link_pattern, markdown_to_html, text)

        # Return None if no match is found
        return None
