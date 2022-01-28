from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os

class AccountManager(BaseUserManager):
    
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have a email address.")
        if not username:
            raise ValueError("User must have a username.")
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
  
def get_profile_image_filepath(self, filename):
    return f'profile_images/{self.pk}/{"profile_image.png"}'

def get_default_profile_image():
    return "profile_images/default_profile_images.png"

def get_coughing_audio_filepath(self, filename):
    return f'coughing_audio{self.pk}{"coughing_audio.wav"}'

def get_default_coughing_audio():
    return "coughing_audio/default_coughing_audio.wav"

class Account(AbstractBaseUser):
    
    email           = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username        = models.CharField(max_length=30, unique=True)
    name            = models.CharField(max_length=64, default="N/A")
    phone           = models.CharField(max_length=12, default="N/A")
    date_joined     = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login      = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    profile_image   = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
    coughing_audio  = models.FileField(upload_to=get_coughing_audio_filepath, null=True, blank=True, default=get_default_coughing_audio)
    diagnose_code   = models.CharField(max_length=1, blank=True)
    hide_email      = models.BooleanField(default=True)
    
    objects = AccountManager()
    
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index(f'profile_images/{self.pk}/')]
    
    def get_coughing_audio_filename(self):
        return str(self.coughing_audio)[str(self.coughing_audio).index(f'coughing_audio/{self.pk}/')]
             
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def get_diagnose_code(self):
        return self.diagnose_code
    
class CoughingResult(models.Model):
    test_date_time = models.CharField(max_length=32, blank=True)
    diagnose_status = models.CharField(max_length=8, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return super().__str__()