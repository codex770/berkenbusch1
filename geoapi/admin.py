from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import PipeNetwork

@admin.register(PipeNetwork)
class PipeNetworkAdmin(GISModelAdmin):
    list_display = ('name',)
