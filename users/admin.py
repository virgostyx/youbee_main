# youbee_main/users/admin.py

# System libraries


# Third party libraries


# Django modules
from django.contrib import admin

# Django apps


# Current app  modules
from .models import User


admin.site.register(User)


