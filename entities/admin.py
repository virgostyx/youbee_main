# youbee_main/entities/admin.py

# System libraries


# Third party libraries


# Django modules
from django.contrib import admin

# Django apps


# Current app  modules
from .models import Entity, EntityDetail, Department, Employee


admin.site.register(Entity)
admin.site.register(EntityDetail)
admin.site.register(Department)
admin.site.register(Employee)
