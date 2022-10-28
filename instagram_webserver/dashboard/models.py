from django.db import models

# Create your models here.

class FacesNew(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    taken_at = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    time_entered = models.CharField(max_length=255, blank=True, null=True)
    date_entered = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faces_new'




class ImagesNew(models.Model):
    username = models.CharField(max_length=255)
    taken_at = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    device_timestamp = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    alt_caption = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    time_entered = models.CharField(max_length=255, blank=True, null=True)
    date_entered = models.CharField(max_length=255, blank=True, null=True)
    faces_extracted = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images_new'
