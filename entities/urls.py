# youbee_main/entities/urls.py

# System libraries

# Third-party libraries

# Django modules
from django.urls import path

# Django apps

#  Current app modules
from .views import (EntityDetailView,
                    CreateDepartmentView,
                    UpdateDepartmentView,
                    DeleteDepartmentView,
                    CreateEmployeeView,
                    DepartmentTableView,
                    EmployeeTableView,
                    UpdateEmployeeView,
                    DeleteEmployeeView,
                    )

app_name = 'entities'

urlpatterns = [
    path('detail/', EntityDetailView.as_view(), name='entity_detail'),
    path('departments/', DepartmentTableView.as_view(), name='entity_departments'),
    path('departments/create', CreateDepartmentView.as_view(), name='create_department'),
    path('departments/<int:pk>/update', UpdateDepartmentView.as_view(), name='update_department'),
    path('departments/<int:pk>/delete', DeleteDepartmentView.as_view(), name='delete_department'),
    path('employees/', EmployeeTableView.as_view(), name='entity_employees'),
    path('employees/create', CreateEmployeeView.as_view(), name='create_employee'),
    path('employees/<int:pk>/update', UpdateEmployeeView.as_view(), name='update_employee'),
    path('employees/<int:pk>/delete', DeleteEmployeeView.as_view(), name='delete_employee'),
]
