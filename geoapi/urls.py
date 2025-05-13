from django.urls import path
from .views import (
    FileUploadView,
    CSVLeakDetectionView,
    LeakDetectionListView,
    MergeDrivingView,
    BoundaryFillView,
    RelateLeaksToPipesView,
    LeakReportListView,
    GenerateLeakReportsView
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('process/leak-detection/', CSVLeakDetectionView.as_view(), name='leak-detection'),
    path('issues/', LeakDetectionListView.as_view(), name='leak-issues'),
    path('process/merge/', MergeDrivingView.as_view(), name='merge-driving'),
    path('process/fill-boundary/', BoundaryFillView.as_view(), name='fill-boundary'),
    path('process/relate-leaks/', RelateLeaksToPipesView.as_view(), name='relate-leaks'),
    path('reports/', LeakReportListView.as_view(), name='leak-reports'),
    path('process/generate-report/', GenerateLeakReportsView.as_view(), name='generate-report'),
]

