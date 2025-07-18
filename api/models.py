from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        app_label = 'api'

class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    query = models.TextField()
    filters = models.JSONField(default=dict)  
    results = models.JSONField(default=list)  
    recommendations = models.JSONField(default=list)  
    search_type = models.CharField(max_length=20, default='search')  
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        app_label = 'api'

class Property(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    bhk = models.IntegerField()
    price = models.IntegerField()
    
    class Meta:
        app_label = 'api'

    def __str__(self):
        return f"{self.bhk}BHK in {self.location} - ₹{self.price}"
