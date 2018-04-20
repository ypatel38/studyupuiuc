from django.db import models

# Create your models here.

#adjacency to built in Django user
# class IsInstructor(models.Model):
#     netID = models.TextField(primary_key=True) #django user has username instead of netID
#     is_instructor = models.BooleanField()


#relationships
# class PartneredWith(models.Model):
#     netID_1 = models.TextField()
#     netID_2 = models.TextField()
#     recent_timestamp = models.DateTimeField(auto_now_add=True) #auto_now saves on all updates
#     number_interactions = models.PositiveIntegerField()
#
#     class Meta:
#         unique_together = (('netID_1', 'netID_2'),)

class EnrolledIn(models.Model):
    netID = models.TextField()
    class_code = models.TextField()

    class Meta:
        unique_together = (('netID', 'class_code'),)
