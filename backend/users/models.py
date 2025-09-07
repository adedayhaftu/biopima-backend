from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
USER_TYPE_CHOICES = [
   ('Consultant', 'Consultant'),
   ('Institutional operator', 'Institutional operator'),

]

class UserManager(BaseUserManager):

   use_in_migrations = True
   def create_user(self, email, password=None, **extra_fields):
       if not email:
              raise ValueError('The Email must be set')
       email = self.normalize_email(email)
       user = self.model(email=email, **extra_fields)
       user.set_password(password)
       user.save(using=self._db)
       return user
   def create_superuser(self, email, password=None, **extra_fields):
       extra_fields.setdefault('is_staff', True)
       extra_fields.setdefault('is_superuser', True)
       extra_fields.setdefault('is_active', True)
       extra_fields.setdefault('user_type', 'Consultant')
       
       if extra_fields.get('is_staff') is not True:
           raise ValueError('Superuser must have is_staff=True.')
       if extra_fields.get('is_superuser') is not True:
           raise ValueError('Superuser must have is_superuser=True.')
       return self.create_user(email, password, **extra_fields)

class Users(AbstractUser):

   name = models.CharField(max_length=255)
#    device = models.ForeignKey('devices.Devices', on_delete=models.SET_NULL, blank=True, null=True)
   image = models.ImageField(upload_to="profiles/", blank=True, null=True)
   email = models.EmailField('email address', unique=True)
   phone_number = models.CharField(max_length=20, blank=True, null=True)
   user_type = models.CharField(max_length=40, choices=USER_TYPE_CHOICES, default='Designer')
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
  
   password = models.CharField(max_length=128)
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)
   is_superuser = models.BooleanField(default=False)


   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['name', 'user_type']
   
   objects = UserManager()

   def __str__(self):
       return f"{self.name} ({self.get_user_type_display()})"


