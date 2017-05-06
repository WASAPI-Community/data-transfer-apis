from django.contrib import admin
from archiveit.wasapi.models import WasapiJob

class WasapiJobAdmin(admin.ModelAdmin):
    search_fields = ['id', 'state', 'function', 'account__id', 'account__organization_name']
    list_display = ['id', 'state', 'function', 'termination_time']

admin.site.register(WasapiJob, WasapiJobAdmin)
