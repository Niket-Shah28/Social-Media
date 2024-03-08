from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from .managers import CustomUserManager

# Create your models here.

class UserProfile(AbstractBaseUser,PermissionsMixin):
    userId = models.UUIDField(default=uuid.uuid4,auto_created=True,primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50,unique=True)
    profilePic = models.ImageField(default='defaultProfilePic.jpg',upload_to='profilePic/')
    bio = models.TextField()
    gender = models.CharField(max_length=10)
    contactNumber = PhoneNumberField()
    created_at = models.DateTimeField(auto_created=True,auto_now=True,editable=False)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.userId)


class Posts(models.Model):
    postId = models.UUIDField(default=uuid.uuid4,auto_created=True,primary_key=True)
    file = models.FileField(upload_to='static/')
    caption = models.CharField(max_length=200)
    userId = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True,auto_now=True)

    def __str__(self):
        return str(self.postId)

class Likes(models.Model):
    postId = models.ForeignKey(Posts,on_delete=models.CASCADE)
    userId = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_created=True,auto_now=True)

class Connections(models.Model):
    connId = models.UUIDField(default=uuid.uuid4,auto_created=True,primary_key=True)
    user1 = models.ForeignKey(UserProfile,related_name="connection_1",on_delete=models.CASCADE)
    user2 = models.ForeignKey(UserProfile,related_name="connection_2",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True,auto_now=True)

    def __str__(self):
        return str(self.connId)

class ConnectionRequest(models.Model):
    reqId = models.UUIDField(default=uuid.uuid4,auto_created=True,primary_key=True)
    source = models.ForeignKey(UserProfile,related_name="connection_request_source",on_delete=models.CASCADE)
    destination = models.ForeignKey(UserProfile,related_name="connection_request_destination",on_delete=models.CASCADE)

    def __str__(self):
        return str(self.reqId)