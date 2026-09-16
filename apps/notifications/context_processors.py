def unread_notifications(request):
    if not request.user.is_authenticated:
        return {}
    from .models import Notification
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    recent = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:6]
    return {"unread_notification_count": count, "recent_notifications": recent}
