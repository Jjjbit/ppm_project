from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_store_manager = models.BooleanField(default=False)
    address = models.TextField(blank=True)

