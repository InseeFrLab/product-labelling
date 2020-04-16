from django.db import models
from django.conf import settings
from django.utils import timezone

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=200)#(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle

class Labellisation(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=200)#(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=200)
    label = models.TextField()
    prediction = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle
