from .models import Notification


def notify(recipient, kind, title, message="", link=""):
    return Notification.objects.create(recipient=recipient, kind=kind, title=title, message=message, link=link)


def notify_many(recipients, kind, title, message="", link=""):
    objs = [Notification(recipient=r, kind=kind, title=title, message=message, link=link) for r in recipients]
    return Notification.objects.bulk_create(objs)
