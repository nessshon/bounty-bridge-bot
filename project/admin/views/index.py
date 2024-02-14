from sqlalchemy import *
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from project.db.models import IssueDB


class IndexView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        session: AsyncSession = request.state.session
        statement = select(IssueDB).limit(10).order_by(desc(IssueDB.created_at))
        result = await session.execute(statement)
        issues = result.scalars().all()

        return templates.TemplateResponse(
            "index.html", {"request": request, "issues": issues}
        )
