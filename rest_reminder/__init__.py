import fire
from rest_reminder import reminder


__all__ = (
    "main"
)


def main():
    def start(interval=None):
        reminder.Reminder(interval).start()

    fire.Fire(start)
