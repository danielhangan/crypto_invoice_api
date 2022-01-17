import uuid
from django.db import models

# Create your models here.
class AppUser(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    coinbase_id = models.CharField(unique=True, max_length=100)
