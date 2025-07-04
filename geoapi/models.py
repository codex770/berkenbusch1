from django.contrib.gis.db import models

class PipeNetwork(models.Model):
    name = models.CharField(max_length=100)
    geometry = models.LineStringField(srid=4326)  # WGS 84 geographic coordinates

    def __str__(self):
        return self.name


class UploadedFile(models.Model):
    FILE_TYPES = (
        ('csv', 'CSV'),
        ('shp', 'Shapefile'),
        ('kml', 'KML'),
        ('geojson', 'GeoJSON'),
        ('unknown', 'Unknown'),
    )

    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='unknown')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    crs = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"



# class LeakDetectionPoint(models.Model):
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#     value = models.FloatField()
#     threshold = models.FloatField(default=0.0)
#     geometry = models.PointField(srid=4326)
#     detected_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Issue @ ({self.latitude}, {self.longitude}) - Value: {self.value}"


# from django.db import models
from django.contrib.gis.db import models as gis_models
from .models import PipeNetwork  # adjust if in separate app

class LeakDetectionPoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    value = models.FloatField()
    threshold = models.FloatField(default=0.0)
    geometry = gis_models.PointField(srid=4326)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    pipe = models.ForeignKey(
        'PipeNetwork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leak_points'
    )

    def __str__(self):
        return f"Issue @ ({self.latitude}, {self.longitude}) - Value: {self.value}"




# class MergedDrivingLine(models.Model):
#     name = models.CharField(max_length=100, default="Merged Line")
#     geometry = models.MultiLineStringField(srid=4326)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name



# models.py
class MergedDrivingLine(models.Model):
    name = models.CharField(max_length=200, default='Merged Drive')
    geometry = models.MultiLineStringField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)




class LeakReport(models.Model):
    pipe = models.ForeignKey(PipeNetwork, on_delete=models.CASCADE)
    leak_count = models.IntegerField()
    total_leak_value = models.FloatField()
    first_detected = models.DateTimeField()
    last_detected = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
