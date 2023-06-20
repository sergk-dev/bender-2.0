from django.db import models

class Bot(models.Model):
    api_key = models.CharField(max_length=100, unique=True, blank=False)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    bot_user_id = models.BigIntegerField(default=0, unique=True)
    
class Community(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200)
    bot = models.ForeignKey(Bot, on_delete=models.DO_NOTHING)

class Prey(models.Model):
    PROGRAM = "prog"
    MY = "my"
    COMMUNITY = "com"
    PREY_TYPE_CHOICES = [
        (PROGRAM, "Program"),
        (MY, "My"),
        (COMMUNITY, "Community"),
    ]
    type = models.CharField(max_length=4, choices=PREY_TYPE_CHOICES, default=PROGRAM)
    name = models.CharField(max_length=100, default="")
    community = models.ForeignKey(Community, on_delete=models.DO_NOTHING)
    text = models.TextField()
    user_id = models.CharField(max_length=50, blank=False)
    
    
