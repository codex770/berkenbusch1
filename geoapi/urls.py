from django.urls import path
from .views import FileUploadView, CSVLeakDetectionView, LeakDetectionListView
from .views import MergeDrivingView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('process/leak-detection/', CSVLeakDetectionView.as_view(), name='leak-detection'),
    path('issues/', LeakDetectionListView.as_view(), name='leak-issues'),
    path('process/merge/', MergeDrivingView.as_view(), name='merge-driving')

]
