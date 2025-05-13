from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'



from .models import LeakDetectionPoint

class LeakDetectionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeakDetectionPoint
        fields = '__all__'


# from .models import MergedDrivingLine
# from rest_framework_gis.serializers import GeoFeatureModelSerializer

# class MergedDrivingLineSerializer(GeoFeatureModelSerializer):
#     class Meta:
#         model = MergedDrivingLine
#         geo_field = 'geometry'
#         fields = ['id', 'name', 'geometry', 'created_at']




# serializers.py
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import MergedDrivingLine

class MergedDrivingLineSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = MergedDrivingLine
        geo_field = 'geometry'
        fields = ['id', 'name', 'created_at']


# serializers.py
from .models import LeakReport
from rest_framework import serializers

class LeakReportSerializer(serializers.ModelSerializer):
    pipe_name = serializers.CharField(source='pipe.name', read_only=True)

    class Meta:
        model = LeakReport
        fields = [
            'id',
            'pipe',
            'pipe_name',
            'leak_count',
            'total_leak_value',
            'first_detected',
            'last_detected',
            'created_at'
        ]

