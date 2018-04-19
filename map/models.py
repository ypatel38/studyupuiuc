from django.db import models

# Create your models here.
class Buildings(models.Model):
    building = models.TextField(primary_key = True)
    address = models.TextField()
