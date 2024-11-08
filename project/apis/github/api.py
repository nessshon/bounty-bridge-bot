import asyncio
from typing import List, Literal, Union

from aiohttp import ClientConnectorError

from .models import Issue
from ..client import ClientAPI


class GitHubAPI(ClientAPI):
    """
    Asynchronous GitHub API client for fetching issue-related data.
    """

    def __init__(
            self,
            token: str,
            owner: str,
            repo: str,
            base_url: str = "https://api.github.com",
    ) -> None:
        """
        Initializes the GitHubAPI object.

        :param token: GitHub API token for authentication.
        :param owner: Owner of the GitHub repository.
        :param repo: GitHub repository name.
        :param base_url: Base URL for GitHub API (default is "https://api.github.com").
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = base_url
        self.headers = {
            f"Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.full+json",
        }
        super().__init__(base_url, headers=self.headers)

    async def get_issue(self, issue_number: int) -> Issue:
        """
        Retrieves information about a specific GitHub issue.

        :param issue_number: Issue number.
        :return: Issue object representing the GitHub issue.
        """
        method = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        result = await self._get(method)
        return Issue(**result)

    async def get_issues(
            self,
            page: int,
            state: Literal['open', 'closed', 'all'],
    ) -> Union[List[Issue], None]:
        """
        Retrieves a list of GitHub issues based on pagination and issue state.

        :param page: Page number.
        :param state: State of the issues (e.g., "open", "closed" or "all").
        :return: List of Issue objects representing the GitHub issues.
        """
        method = f"/repos/{self.owner}/{self.repo}/issues"
        params = {"state": state, "page": page, "sort": "created", "direction": "desc", "per_page": 100}
        results = await self._get(method, params=params)
        if not results:
            return None
        return [Issue(**result) for result in results if not result.get('pull_request')]

    async def get_issues_all(self, state: Literal['open', 'closed', 'all']) -> List[Issue]:
        """
        Retrieves all GitHub issues based on the specified state.

        :param state: State of the issues (e.g., "open" or "closed").
        :return: List of Issue objects representing all GitHub issues.
        """
        page, issues = 1, []

        async def _get_issues(p, s):
            try:
                return await self.get_issues(p, s)
            except ClientConnectorError as e:
                if "Cannot connect to host api.github.com" in str(e):
                    await asyncio.sleep(1)
                    return await _get_issues(p, s)
                raise e

        while True:
            results = await _get_issues(page, state)
            if not results:
                break
            issues.extend(results)
            page += 1
        return issues
