# 🚀 Berkenbusch GeoDjango Backend

This project is a GeoDjango-based backend for processing GIS data uploaded from field teams. It supports file uploads (CSV, KML, SHP), automated leak detection, GPS trace merging, and more — all powered by PostGIS.

---

## 📦 Features

- Upload CSV, SHP, KML/KMZ, GeoJSON files
- Automated CRS detection
- Leak detection from CSVs (Schadensfinder logic)
- Merge GPS lines from KML (MergeDriving logic)
- Fully RESTful API for integration with frontend (Leaflet/OpenLayers)
- GeoJSON-ready output for map rendering

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/codex770/berkenbusch1.git
cd berkenbusch1




### 2. Create and activate virtual environment
```bash
python3 -m venv geodjango-env
source geodjango-env/bin/activate



### 3. Install dependencies
```bash
pip install -r requirements.txt
If requirements.txt doesn't exist yet, generate it:

```bash
pip freeze > requirements.txt


### 4. Apply migrations
bash
python manage.py makemigrations
python manage.py migrate


5. Run the development server
bash
python manage.py runserver




🔌 API Endpoints
Method	Endpoint	Description
POST	/api/upload/	Upload any file (.csv, .kml, .shp, etc)
POST	/api/process/leak-detection/	Run leak detection on uploaded CSV
POST	/api/process/merge/	Merge GPS traces from KML/KMZ
GET	/api/issues/	List all detected leak points

💾 Database
Backend: PostgreSQL + PostGIS

Uses Django ORM

Spatial data stored in geometry fields

📍 Next Steps
 Add polygon filling from KML (BoundaryFiller)

 Relate leaks to pipe segments

 Add report generation (PDF + CSV)

👨‍💻 Author
Junaid Rana
github.com/codex770



# GeoBackend - Leak Detection & GIS Processing

A Django + PostGIS backend system to automate GIS workflows, leak detection, and geospatial data reporting.

---

## ✅ Features Implemented

- Upload & process CSV data from sensor logs
- Detect leaks using configurable thresholds
- Store leak points with geometry (EPSG:4326)
- View issues via REST API (`/api/issues/`)
- Environment setup with GeoDjango + GDAL + PostGIS

---

## ⚙️ Setup Instructions

1. Clone the repo:
```bash
git clone <your-repo-url>
cd geo_backend
