from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Notification(models.Model):
    title = models.CharField(max_length=256)
    message = models.TextField()
    viewed = models.BooleanField(default = False)

def send_now(users, title, viewed = False):
    """
    Creates a new notification.
    This is intended to be how other apps create new notices.
    notification.send(user, "friends_invite_sent", {
        "spam": "eggs",
        "foo": "bar",
    )
    """



    # reset environment to original language
    return sent
