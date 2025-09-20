import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def daily_task(self):
    """
    Daily task that runs scheduled maintenance and updates.
    Includes error handling and automatic retries.
    """
    try:
        logger.info("Starting daily task execution")

        # This is a placeholder for your daily task logic.
        # For example, you might update streaks, send notifications, etc.
        logger.info("Running daily task...")
        # Example: update_streaks()
        # Example: send_daily_notifications()

        logger.info("Daily task completed successfully")
        return True

    except Exception as e:
        logger.error(f"Daily task failed: {str(e)}", exc_info=True)
        # Retry the task with exponential backoff
        retry_in = (self.request.retries + 1) * 60  # Wait 1, 2, 3 minutes
        raise self.retry(exc=e, countdown=retry_in) from e
