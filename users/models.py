from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_store_manager = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    #store_name = models.CharField(max_length=255, blank=True)

