import uuid, datetime
from django.db import models

# Create your models here.

#entity sets
class StudySession(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    building = models.TextField()
    room_number = models.PositiveSmallIntegerField()
    description = models.TextField()
    seshID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Notification(models.Model):
    created = models.DateTimeField(auto_now_add=True) #auto_now_add saves on first create
    is_read = models.BooleanField()
    notID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seshID = models.UUIDField(editable=False)


# class OfficeHours(models.Model):
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     date = models.DateField()
#     building = models.TextField()
#     room_number = models.PositiveSmallIntegerField()
#     ohID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class Classes(models.Model):
    class_code = models.TextField(primary_key=True)
    class_name = models.TextField()

# class Section(models.Model):
#     crn = models.PositiveIntegerField(primary_key = True)
#     instructor = models.TextField()
#     location = models.TextField()
#     type = models.TextField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     day = models.TextField()

#relationships
class SessionHas(models.Model):
    netID = models.TextField()
    is_owner = models.BooleanField()
    seshID = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = (('netID', 'seshID'),)

class ClassOfSession(models.Model):
    class_code = models.UUIDField(default=uuid.uuid4, editable=False)
    seshID = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = (('class_code', 'seshID'),)

class SentFrom(models.Model):
    netID = models.TextField()
    notID = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = (('netID', 'notID'),)

class SentTo(models.Model):
    netID = models.TextField()
    notID = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = (('netID', 'notID'),)

# class OfficeHoursOf(models.Model):
#     netID = models.TextField()
#     ohID = models.UUIDField(default=uuid.uuid4, editable=False)
#
#     class Meta:
#         unique_together = (('netID', 'ohID'),)

# class OfficeHourTopic(models.Model):
#     class_code = models.TextField()
#     ohID = models.UUIDField(default=uuid.uuid4, editable=False)
#
#     class Meta:
#         unique_together = (('class_code', 'ohID'),)

# class SectionOf(models.Model):
#     class_code = models.TextField()
#     crn = models.PositiveIntegerField()
#
#     class Meta:
#         unique_together = (('class_code', 'crn'))

class NotificationOf(models.Model):
    notID = models.TextField()
    seshID = models.PositiveIntegerField()

    class Meta:
        unique_together = (('notID', 'seshID'))
