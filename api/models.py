from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager
from jsonfield import JSONField


# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField( max_length=100)
    last_name = models.CharField(max_length=200)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def __str__(self):
        return self.email


class Post(models.Model):
	appky=models.CharField(max_length = 50)


class Adset(models.Model):
	id=models.BigIntegerField(primary_key=True)
	start_time=models.DateTimeField()
	end_time=models.DateTimeField()
	targeting=JSONField(max_length=200)


class AdsetOrignal(models.Model):
    id=models.BigIntegerField(primary_key=True)
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    targeting=JSONField(max_length=200)

class Adset_updte_hours(models.Model):
    id=models.BigIntegerField(primary_key=True)
    user_id=models.BigIntegerField()
    access_token=models.CharField(max_length=1000)
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    targeting=JSONField(max_length=200)