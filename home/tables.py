# project_name/app_module/file_name.py

# System libraries

# Third-party libraries
from django_tables2 import tables
from django_tables2.columns import TemplateColumn, Column

# Django modules
from django.db.models import Count

# Django apps
from entities.models import Department, Employee

#  Current app modules


class DepartmentDashboardTable(tables.Table):
    class Meta:
        model = Department
        exclude = ['id', 'entity']
        order_by = ['name', ]
        empty_text = 'No Department yet. Click Add to create one'

    name = Column(
        footer='Total:',
    )
    employee_count = Column(
        verbose_name="Employees#",
        orderable=True,
        footer=lambda table: sum(x.employee_count for x in table.data),
    )

    def order_employee_count(self, queryset, is_descending):
        queryset = queryset.annotate(count=Count('employees'))\
                           .order_by(("-" if is_descending else "") + "count")
        return queryset, True


class FullNameColumn(Column):
    def render_footer(self, bound_column, table):
        return 'Employees#'


class DepartmentColumn(Column):
    def render_footer(self, bound_column, table):
        q = table.data.data
        return len(q) + 1


class EmployeeDashboardTable(tables.Table):
    class Meta:
        model = Employee
        fields = ['title', 'full_name', 'department', 'user__email', 'roles', ]
        order_by = ['full_name']
        template_name = 'home/table-employee-model.html'
        empty_text = 'No employee yet. Click Add to create one'
        per_page = 9

    full_name = FullNameColumn()
    department = DepartmentColumn()
    roles = TemplateColumn(
        template_name="entities/includes/_roles_cell.html",
        verbose_name="Roles",
        orderable=False,
    )

    def order_full_name(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "user__last_name")
        return queryset, True
