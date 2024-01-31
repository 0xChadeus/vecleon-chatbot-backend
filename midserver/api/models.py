from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

# Create your models here.
class CharacterCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=10000)
    first_message = models.CharField(max_length=10000)
    personality_summary = models.CharField(max_length=10000)
    scenario = models.CharField(max_length=10000)
    src=models.CharField(max_length=500)
    user_key = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

class WorldCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=10000)
    scenario = models.CharField(max_length=10000)
    src=models.CharField(max_length=500)
    user_key = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    msg_history = ArrayField(ArrayField(models.TextField(), size=5))
    user_key = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    character_key = models.ForeignKey(CharacterCard, on_delete=models.CASCADE, null=False)


