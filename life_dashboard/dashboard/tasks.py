from celery import shared_task


@shared_task
def daily_task():
    # This is a placeholder for your daily task logic.
    # For example, you might update streaks, send notifications, etc.
    print("Running daily task...")
    # Example: update_streaks()
    # Example: send_daily_notifications()
