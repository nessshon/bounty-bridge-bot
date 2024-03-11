from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from project.scheduler import Scheduler


class SchedulerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing the scheduler.
    """

    def __init__(self, scheduler: Scheduler, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.scheduler = scheduler

    async def dispatch(self, request, call_next) -> Response:
        """
        Dispatch the request and manage the database session.

        :param request: The request object.
        :param call_next: The next request-response call.
        :return: The response from the next call.
        """
        request.state.scheduler = self.scheduler.scheduler
        response = await call_next(request)
        return response
