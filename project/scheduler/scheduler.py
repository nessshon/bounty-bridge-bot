from typing import Union
from apscheduler.job import Job
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR

from . import tasks
from .errors import on_job_error
from ..config import Config


class Scheduler:
    """
    A class representing a scheduler for managing and running jobs using AsyncIOScheduler.

    Parameters:
    - redis (config): The Config object.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the Scheduler.

        :param config: The Config object.
        """
        self.job_store = RedisJobStore(
            host=config.redis.HOST,
            port=config.redis.PORT,
            db=config.redis.DB + 1,
        )
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': self.job_store},
        )

    def get_all_job_ids(self) -> list[str]:
        """
        Get a list of all job IDs.

        :return: List of job IDs.
        """
        return [job.id for job in self.scheduler.get_jobs()]

    def _delete_job(self, job_id: str) -> Union[Job, None]:
        """
        Delete a job with the given ID.

        :param job_id: The ID of the job to be deleted.
        :return: Deleted Job object or None if the job doesn't exist.
        """
        if job_id not in self.get_all_job_ids():
            return None
        return self.scheduler.remove_job(job_id)

    def _add_track_and_notify_issue(self) -> Job:
        """
        Add a job for tracking and notifying issues at a 2-minute interval.

        :return: The added Job object.
        """
        job_id = tasks.track_and_notify.__name__
        self._delete_job(job_id)
        return self.scheduler.add_job(
            func=tasks.track_and_notify,
            trigger="interval",
            minutes=2,
            id=job_id,
        )

    def _add_weekly_update_digest(self) -> Job:
        """
        Add a job for weekly update of digest on Mondays at 10:00 AM.

        :return: The added Job object.
        """
        job_id = tasks.weekly_update_digest.__name__
        self._delete_job(job_id)
        return self.scheduler.add_job(
            func=tasks.weekly_update_digest,
            trigger="cron",
            day_of_week="mon",
            hour=10,
            minute=0,
            id=job_id,
        )

    def run(self) -> None:
        """
        Start the scheduler and add the track_and_notify_issue job.
        """
        self.scheduler.start()
        self.scheduler.add_listener(on_job_error, mask=EVENT_JOB_ERROR)
        self._add_weekly_update_digest()
        self._add_track_and_notify_issue()

    def shutdown(self) -> None:
        """
        Shutdown the scheduler and delete both jobs.
        """
        self._delete_job(tasks.weekly_update_digest.__name__)
        self._delete_job(tasks.track_and_notify.__name__)
        self.scheduler.shutdown()
