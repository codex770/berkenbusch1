from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedFile, LeakDetectionPoint
from .serializers import UploadedFileSerializer
from django.contrib.gis.geos import Point
import pandas as pd
import os
import io

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



class CSVLeakDetectionView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file or not uploaded_file.name.endswith('.csv'):
            return Response({'error': 'Only .csv files are supported'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode and parse the CSV (semicolon delimiter, comma decimals)
            decoded = uploaded_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(decoded), delimiter=';', engine='python')

            # Replace comma decimals with dots and convert to numeric
            for col in df.columns:
                if df[col].astype(str).str.contains(',').any():
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

            df = df.where(pd.notnull(df), None)

            # ✅ Rename actual columns to match expected names
            df = df.rename(columns={
                'X': 'latitude',
                'Y': 'longitude',
                'MethanMesswert': 'value'
            })

        except Exception as e:
            return Response({'error': f'CSV parsing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        required = {'latitude', 'longitude', 'value'}
        if not required.issubset(df.columns):
            return Response({'error': f'Missing required columns: {required}'}, status=status.HTTP_400_BAD_REQUEST)

        threshold = 30
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


from rest_framework.generics import ListAPIView
from .serializers import LeakDetectionPointSerializer

class LeakDetectionListView(ListAPIView):
    queryset = LeakDetectionPoint.objects.all()
    serializer_class = LeakDetectionPointSerializer













import os
import zipfile
import tempfile
import geopandas as gpd
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import pyogrio


class MergeDrivingView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            print("❌ No file received.")
            return JsonResponse({"error": "No file uploaded"}, status=400)

        print(f"✅ Received file: {uploaded_file.name}")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                kmz_path = os.path.join(tmpdir, uploaded_file.name)

                with open(kmz_path, "wb") as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                print("📦 Extracting KMZ...")
                with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)

                kml_path = os.path.join(tmpdir, "doc.kml")
                print(f"📄 KML path: {kml_path}")

                if not os.path.exists(kml_path):
                    return JsonResponse({"error": "KML file not found in KMZ."}, status=400)

                print("🔍 Listing layers...")
                layers = pyogrio.list_layers(kml_path)
                print("📚 Found layers:", layers)

                if "Route" not in layers:
                    return JsonResponse({"error": "'Route' layer not found in KML."}, status=400)

                print("📊 Reading 'Route' layer...")
                gdf = gpd.read_file(kml_path, layer="Route")
                print("✅ Parsed KML. Number of features:", len(gdf))

                lines = gdf[gdf.geometry.type == "LineString"]

                if lines.empty:
                    print("⚠️ No LineStrings found.")
                    return JsonResponse({"error": "No line geometries found."}, status=400)

                merged = lines.unary_union

                result_gdf = gpd.GeoDataFrame(geometry=[merged], crs=lines.crs)
                geojson = result_gdf.to_json()

                print("✅ Merged line geometry created.")
                return JsonResponse({"merged_geojson": geojson}, status=200)

        except Exception as e:
            print("🔥 Error:", str(e))
            return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)
