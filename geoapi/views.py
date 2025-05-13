# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import UploadedFile, LeakDetectionPoint
# from .serializers import UploadedFileSerializer
# from django.contrib.gis.geos import Point
# import pandas as pd
# import os
# import io

# class FileUploadView(APIView):
#     def post(self, request, *args, **kwargs):
#         uploaded_file = request.FILES.get('file')
#         if not uploaded_file:
#             return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

#         ext = os.path.splitext(uploaded_file.name)[1].lower()
#         ext_map = {
#             '.csv': 'csv',
#             '.shp': 'shp',
#             '.kml': 'kml',
#             '.geojson': 'geojson',
#         }
#         file_type = ext_map.get(ext, 'unknown')

#         instance = UploadedFile.objects.create(file=uploaded_file, file_type=file_type)
#         serializer = UploadedFileSerializer(instance)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)



# class CSVLeakDetectionView(APIView):
#     def post(self, request, *args, **kwargs):
#         uploaded_file = request.FILES.get('file')
#         if not uploaded_file or not uploaded_file.name.endswith('.csv'):
#             return Response({'error': 'Only .csv files are supported'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Decode and parse the CSV (semicolon delimiter, comma decimals)
#             decoded = uploaded_file.read().decode('utf-8')
#             df = pd.read_csv(io.StringIO(decoded), delimiter=';', engine='python')

#             # Replace comma decimals with dots and convert to numeric
#             for col in df.columns:
#                 if df[col].astype(str).str.contains(',').any():
#                     df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

#             df = df.where(pd.notnull(df), None)

#             # ✅ Rename actual columns to match expected names
#             df = df.rename(columns={
#                 'X': 'latitude',
#                 'Y': 'longitude',
#                 'MethanMesswert': 'value'
#             })

#         except Exception as e:
#             return Response({'error': f'CSV parsing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

#         required = {'latitude', 'longitude', 'value'}
#         if not required.issubset(df.columns):
#             return Response({'error': f'Missing required columns: {required}'}, status=status.HTTP_400_BAD_REQUEST)

#         threshold = 30
#         created = 0

#         for _, row in df.iterrows():
#             if row['value'] >= threshold:
#                 LeakDetectionPoint.objects.create(
#                     latitude=row['latitude'],
#                     longitude=row['longitude'],
#                     value=row['value'],
#                     threshold=threshold,
#                     geometry=Point(row['longitude'], row['latitude'])
#                 )
#                 created += 1

#         return Response({'message': f'{created} leak(s) detected and stored.'}, status=status.HTTP_201_CREATED)


# from rest_framework.generics import ListAPIView
# from .serializers import LeakDetectionPointSerializer

# class LeakDetectionListView(ListAPIView):
#     queryset = LeakDetectionPoint.objects.all()
#     serializer_class = LeakDetectionPointSerializer













# import os
# import zipfile
# import tempfile
# import geopandas as gpd
# from django.http import JsonResponse
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework import status
# import pyogrio


# class MergeDrivingView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request, *args, **kwargs):
#         uploaded_file = request.FILES.get("file")
#         if not uploaded_file:
#             print("❌ No file received.")
#             return JsonResponse({"error": "No file uploaded"}, status=400)

#         print(f"✅ Received file: {uploaded_file.name}")

#         try:
#             with tempfile.TemporaryDirectory() as tmpdir:
#                 kmz_path = os.path.join(tmpdir, uploaded_file.name)

#                 with open(kmz_path, "wb") as f:
#                     for chunk in uploaded_file.chunks():
#                         f.write(chunk)

#                 print("📦 Extracting KMZ...")
#                 with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
#                     zip_ref.extractall(tmpdir)

#                 kml_path = os.path.join(tmpdir, "doc.kml")
#                 print(f"📄 KML path: {kml_path}")

#                 if not os.path.exists(kml_path):
#                     return JsonResponse({"error": "KML file not found in KMZ."}, status=400)

#                 print("🔍 Listing layers...")
#                 layers = pyogrio.list_layers(kml_path)
#                 print("📚 Found layers:", layers)

#                 if "Route" not in layers:
#                     return JsonResponse({"error": "'Route' layer not found in KML."}, status=400)

#                 print("📊 Reading 'Route' layer...")
#                 gdf = gpd.read_file(kml_path, layer="Route")
#                 print("✅ Parsed KML. Number of features:", len(gdf))

#                 lines = gdf[gdf.geometry.type == "LineString"]

#                 if lines.empty:
#                     print("⚠️ No LineStrings found.")
#                     return JsonResponse({"error": "No line geometries found."}, status=400)

#                 merged = lines.unary_union

#                 result_gdf = gpd.GeoDataFrame(geometry=[merged], crs=lines.crs)
#                 geojson = result_gdf.to_json()

#                 print("✅ Merged line geometry created.")
#                 return JsonResponse({"merged_geojson": geojson}, status=200)

#         except Exception as e:
#             print("🔥 Error:", str(e))
#             return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)


# import shapely
# from shapely.geometry import Polygon
# from django.http import JsonResponse

# class BoundaryFillView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request, *args, **kwargs):
#         uploaded_file = request.FILES.get("file")
#         if not uploaded_file:
#             return JsonResponse({"error": "No file uploaded"}, status=400)

#         print(f"📁 Received file: {uploaded_file.name}")

#         try:
#             with tempfile.TemporaryDirectory() as tmpdir:
#                 zip_path = os.path.join(tmpdir, uploaded_file.name)

#                 with open(zip_path, "wb") as f:
#                     for chunk in uploaded_file.chunks():
#                         f.write(chunk)

#                 print("📦 Extracting...")
#                 with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                     zip_ref.extractall(tmpdir)

#                 kml_path = os.path.join(tmpdir, "doc.kml")
#                 print(f"📄 Looking for KML: {kml_path}")

#                 if not os.path.exists(kml_path):
#                     return JsonResponse({"error": "KML file not found."}, status=400)

#                 print("🔍 Reading KML...")
#                 gdf = gpd.read_file(kml_path, layer="Covered Area")
#                 print("✅ Features loaded:", len(gdf))

#                 # Extract valid polygons
#                 polygons = gdf[gdf.geometry.type == "Polygon"].geometry

#                 if polygons.empty:
#                     return JsonResponse({"error": "No polygons found."}, status=400)

#                 print("🔄 Merging polygons...")
#                 merged = shapely.ops.unary_union(polygons)

#                 filled_gdf = gpd.GeoDataFrame(geometry=[merged], crs=gdf.crs)
#                 geojson = filled_gdf.to_json()

#                 print("✅ Polygon filling done.")
#                 return JsonResponse({"filled_boundary_geojson": geojson}, status=200)

#         except Exception as e:
#             print("🔥 Error during boundary fill:", str(e))
#             return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)








# from django.contrib.gis.db.models.functions import Distance
# from .models import PipeNetwork

# def find_nearest_pipe(point_geometry, max_distance=50):  # meters
#     nearby_pipe = (
#         PipeNetwork.objects
#         .annotate(distance=Distance('geometry', point_geometry))
#         .filter(geometry__distance_lte=(point_geometry, max_distance))
#         .order_by('distance')
#         .first()
#     )
#     return nearby_pipe



# # from rest_framework.views import APIView
# # from rest_framework.response import Response

# # class RelateLeaksToPipesView(APIView):
# #     def post(self, request, *args, **kwargs):
# #         return Response({"message": "Relating leaks to pipes is not implemented yet."})
    




# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import LeakDetectionPoint
# from .utils import find_nearest_pipe  # if you moved it to utils.py, otherwise import directly

# class RelateLeaksToPipesView(APIView):
#     def post(self, request, *args, **kwargs):
#         matched = 0
#         for leak in LeakDetectionPoint.objects.all():
#             if not leak.pipe:
#                 nearest_pipe = find_nearest_pipe(leak.geometry)
#                 if nearest_pipe:
#                     leak.pipe = nearest_pipe
#                     leak.save()
#                     matched += 1

#         return Response({"message": f"{matched} leaks matched to nearest pipe segments."})


























import os
import io
import zipfile
import tempfile
import pandas as pd
import geopandas as gpd
import shapely
# from shapely.geometry import Point, Polygon
from django.contrib.gis.geos import Point

import pyogrio

from django.http import JsonResponse
from django.contrib.gis.db.models.functions import Distance
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import UploadedFile, LeakDetectionPoint, PipeNetwork
from .serializers import UploadedFileSerializer, LeakDetectionPointSerializer


# -------------------- FILE UPLOAD --------------------
class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        ext_map = {
            '.csv': 'csv',
            '.shp': 'shp',
            '.kml': 'kml',
            '.geojson': 'geojson',
        }
        file_type = ext_map.get(ext, 'unknown')

        instance = UploadedFile.objects.create(file=uploaded_file, file_type=file_type)
        serializer = UploadedFileSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -------------------- CSV LEAK DETECTION --------------------
class CSVLeakDetectionView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file or not uploaded_file.name.endswith('.csv'):
            return Response({'error': 'Only .csv files are supported'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = uploaded_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(decoded), delimiter=';', engine='python')
            for col in df.columns:
                if df[col].astype(str).str.contains(',').any():
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

            df = df.where(pd.notnull(df), None)
            df = df.rename(columns={'X': 'latitude', 'Y': 'longitude', 'MethanMesswert': 'value'})

        except Exception as e:
            return Response({'error': f'CSV parsing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        required = {'latitude', 'longitude', 'value'}
        if not required.issubset(df.columns):
            return Response({'error': f'Missing required columns: {required}'}, status=status.HTTP_400_BAD_REQUEST)

        threshold = 1
        created = 0

        for _, row in df.iterrows():
            if row['value'] >= threshold:
                LeakDetectionPoint.objects.create(
                    latitude=row['latitude'],
                    longitude=row['longitude'],
                    value=row['value'],
                    threshold=threshold,
                    geometry=Point(row['longitude'], row['latitude'])
                )
                created += 1

        return Response({'message': f'{created} leak(s) detected and stored.'}, status=status.HTTP_201_CREATED)


# -------------------- LIST LEAKS --------------------
class LeakDetectionListView(ListAPIView):
    queryset = LeakDetectionPoint.objects.all()
    serializer_class = LeakDetectionPointSerializer


# -------------------- MERGE GPS LINES --------------------
class MergeDrivingView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                kmz_path = os.path.join(tmpdir, uploaded_file.name)
                with open(kmz_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)

                kml_path = os.path.join(tmpdir, "doc.kml")
                if not os.path.exists(kml_path):
                    return JsonResponse({"error": "KML file not found in KMZ."}, status=400)

                layers = pyogrio.list_layers(kml_path)
                if "Route" not in layers:
                    return JsonResponse({"error": "'Route' layer not found in KML."}, status=400)

                gdf = gpd.read_file(kml_path, layer="Route")
                lines = gdf[gdf.geometry.type == "LineString"]
                if lines.empty:
                    return JsonResponse({"error": "No line geometries found."}, status=400)

                merged = lines.unary_union
                result_gdf = gpd.GeoDataFrame(geometry=[merged], crs=lines.crs)
                geojson = result_gdf.to_json()

                return JsonResponse({"merged_geojson": geojson}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)


# -------------------- FILL BOUNDARY --------------------
class BoundaryFillView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, uploaded_file.name)
                with open(zip_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)

                kml_path = os.path.join(tmpdir, "doc.kml")
                if not os.path.exists(kml_path):
                    return JsonResponse({"error": "KML file not found."}, status=400)

                gdf = gpd.read_file(kml_path, layer="Covered Area")
                polygons = gdf[gdf.geometry.type == "Polygon"].geometry
                if polygons.empty:
                    return JsonResponse({"error": "No polygons found."}, status=400)

                merged = shapely.ops.unary_union(polygons)
                filled_gdf = gpd.GeoDataFrame(geometry=[merged], crs=gdf.crs)
                geojson = filled_gdf.to_json()

                return JsonResponse({"filled_boundary_geojson": geojson}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)


# -------------------- RELATE LEAKS TO PIPES --------------------
def find_nearest_pipe(point_geometry, max_distance=1):
    return (
        PipeNetwork.objects
        .annotate(distance=Distance('geometry', point_geometry))
        .filter(geometry__distance_lte=(point_geometry, max_distance))
        .order_by('distance')
        .first()
    )

class RelateLeaksToPipesView(APIView):
    def post(self, request, *args, **kwargs):
        matched = 0
        leaks = LeakDetectionPoint.objects.filter(pipe__isnull=True)

        for leak in leaks:
            nearest_pipe = find_nearest_pipe(leak.geometry)
            if nearest_pipe:
                leak.pipe = nearest_pipe
                leak.save()
                matched += 1

        return Response({"message": f"{matched} leaks matched to nearest pipe segments."})




from .models import LeakReport, PipeNetwork, LeakDetectionPoint
from .serializers import LeakReportSerializer
from django.utils.timezone import now

class LeakReportListView(ListAPIView):
    queryset = LeakReport.objects.all()
    serializer_class = LeakReportSerializer


class GenerateLeakReportsView(APIView):
    def post(self, request, *args, **kwargs):
        created = 0
        for pipe in PipeNetwork.objects.all():
            leaks = LeakDetectionPoint.objects.filter(geometry__distance_lte=(pipe.geometry, 50))
            if not leaks.exists():
                continue
            report = LeakReport.objects.create(
                pipe=pipe,
                leak_count=leaks.count(),
                total_leak_value=sum([l.value for l in leaks]),
                first_detected=min([l.detected_at for l in leaks]),
                last_detected=max([l.detected_at for l in leaks]),
            )
            created += 1
        return Response({"message": f"{created} report(s) generated."})


