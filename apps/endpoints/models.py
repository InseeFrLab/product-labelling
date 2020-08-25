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

class Label(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=200)
    label_in = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle

class labellingByHand(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=200)
    label_in = models.CharField(max_length=100000)
    label_out = models.TextField()
    probability = models.FloatField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle

class labellingToDo(models.Model):
    id = models.AutoField(primary_key=True)
    label_in = models.CharField(max_length=100000)
    table_name = models.TextField(blank=True, null=True)
    categ = models.TextField(blank=True, null=True)
    ean = models.TextField(blank=True, null=True)
    ongoing = models.PositiveIntegerField(blank=True, default=0)
    labeled = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle

class labellingOnGoing(models.Model):
    id = models.AutoField(primary_key=True)
    id_label=models.IntegerField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle

class labellingDone(models.Model):
    id = models.AutoField(primary_key=True)
    id_label = models.IntegerField(blank=True, null=True)
    label_in = models.CharField(max_length=100000)
    categ = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    label_out = models.TextField(blank=True, null=True)
    probability = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)
    unknown = models.BooleanField(blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.libelle
