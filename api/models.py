from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.contrib.auth import get_user_model
from django.conf import settings 

# Create your models here.
User = settings.AUTH_USER_MODEL



class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=True) 
    email = models.EmailField(unique=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.username





class List(models.Model):
    list_title= models.CharField(max_length=50)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    def save(self, *args, **kwargs):

        self.list_title = ' '.join(self.list_title.split())
        self.list_title = self.list_title.strip()
        self.list_title = self.list_title.lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.list_title


class Task(models.Model):
    HIGH= 1
    LOW=2

    PRIORITY_CHOICES = (
        (HIGH, 'High'),
        (LOW, 'Low')
    )
    list_id = models.ForeignKey(List,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200,default='',blank=True,null=True)
    due_date = models.DateField()
    is_Completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(choices= PRIORITY_CHOICES,default=LOW)

    def __str__(self):
        return f"{self.title}"  #self.get_priority_display() will return the value if used
     
    class Meta:
        ordering = ['priority']