"""Models for the SEEKER app.

"""
from django.db import models
from django.utils import timezone

# Create your models here.

def get_current_datetime():
    """Get the current time"""
    return timezone.now()

