from django.contrib import admin
from django.urls import path, include  # ← Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('geoapi.urls')),  # ← ✅ This connects your upload view
]
