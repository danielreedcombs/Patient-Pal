from django.contrib.auth.models import User
from django.db import models

# Models for the SQL database
class medication(models.Model):
    patient = models.ForeignKey(User , on_delete=models.CASCADE, null=True)
    name =  models.CharField(max_length = 200, null=True)
    dosage = models.CharField(max_length = 200, null=True)
    deletedOn = models.CharField(max_length=100 , null=True)

class doctors_visits(models.Model):
    patient = models.ForeignKey(User , on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=200, null=True)
    date= models.DateField(null=True, blank=True)
    time = models.TimeField(null=True , blank=True)
    doctors_name = models.CharField(max_length=200 , null=True)
    deletedOn = models.CharField(max_length=100 , null=True)


class Notes(models.Model):
    user = models.ForeignKey(User , on_delete= models.CASCADE , null=True)
    note = models.CharField(max_length=750)
    deletedOn = models.CharField(max_length=100 , null=True)
    doctors_visits = models.ManyToManyField(doctors_visits , blank=True, through='doctors_notes')

class doctors_notes(models.Model):
    notes = models.ForeignKey(Notes , on_delete=models.CASCADE , null=True)
    doctors_vist = models.ForeignKey( doctors_visits , on_delete=models.CASCADE , null=True)
    deletedOn = models.CharField(max_length=100 , null=True)

