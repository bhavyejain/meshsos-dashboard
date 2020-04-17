import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Log(models.Model):
    # server_db_id : id of log in server db
    server_db_id = models.IntegerField()

    # string of format "%Y-%m-%d %H:%M:%S" eg. "2020-04-01 20:01:14", FORMAT = UTC
    timestamp = models.CharField(max_length=19, default='-')

    # emergency_ype contains string one of 'medical' & 'police'
    emergency_type = models.CharField(max_length=7, default='-')

    # core_id: id of sending device
    core_id = models.CharField(max_length=30, default='-')

    # latitude and longitude
    latitude = models.FloatField(default=-1.0)
    longitude = models.FloatField(default=-1.0)

    # accuracy
    accuracy = models.FloatField()

    # status: one of string: 'a' (active), 'w' (working), 'r' (resolved)
    status = models.CharField(max_length=1, default='a')

    def __str__(self):
        return str(self.id) + " " + str(self.timestamp) + " " + str(self.core_id)

    def save_log(self):
        self.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.TextField(max_length=500, blank=True)         # user.profile.location
    service = models.CharField(max_length=8, blank=True)            # user.profile.service
    phone = models.CharField(max_length=13, blank=True)             # user.profile.phone


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()