from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone as django_timezone
from datetime import timedelta
from dotenv import load_dotenv

from apps.user.managers import UserManager
import os

load_dotenv()

def default_created_at():
    tz = os.getenv("TIMEZONE_HOURS")
    if tz.strip().startswith("-"):
        return django_timezone.now() - timedelta(hours=int(tz.replace("-","").strip()))
    return django_timezone.now() + timedelta(hours=int(tz))

class User(AbstractBaseUser):
    SEXE_CHOICE = [
        ('M', 'Masculin'),
        ('F', 'Feminin'),
        ('I', 'Inconnu')
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICE, default='I')
    password = models.CharField(max_length=250)
    profession_domaine = models.CharField(max_length=100)
    birth_date = models.DateField()
    profile = models.ImageField(upload_to='users/profiles', default='users/profiles/default.png')
    code_id = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=django_timezone.now)
    
    USERNAME = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'birth_date', 'sexe']
    
    objects = UserManager()
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'user'