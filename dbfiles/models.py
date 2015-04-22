from django.db import models

# used by storage class
class DbFile(models.Model):
    name = models.CharField(max_length=512, primary_key=True)
    blob = models.BinaryField()
    size = models.IntegerField()
    accessed = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
