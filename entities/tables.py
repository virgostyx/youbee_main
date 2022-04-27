# youbee_main/entities/tables.py

# System libraries

# Third-party libraries
from django_tables2 import tables
from django_tables2.views import SingleTableView
from django_tables2.columns import TemplateColumn, Column

# Django modules
from django.db.models import Count

# Django apps
from entities.models import Department, Employee


#  Current app modules


class SingleTableWithCaptionView(SingleTableView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return context


class DepartmentTable(tables.Table):
    class Meta:
        model = Department
        exclude = ['id', 'entity']
        order_by = ['name', ]
        template_name = 'entities/table-caption-model.html'
        attrs = {"class": "lcars-table lcars-golden-tanoi-color special-caption"}
        empty_text = 'No Department yet. Click Add to create one'
        per_page = 10

    caption = 'DEPARTMENTS'

    name = Column(
        footer='Total:',
    )
    employee_count = Column(
        verbose_name="Employees#",
        orderable=True,
        footer=lambda table: sum(x.employee_count for x in table.data),
    )
    buttons = TemplateColumn(
        template_name="entities/includes/_department_actions_buttons.html",
        verbose_name="Actions",
        orderable=False,
    )

    def order_employee_count(self, queryset, is_descending):
        queryset = queryset.annotate(count=Count('employees'))\
                           .order_by(("-" if is_descending else "") + "count")
        return (queryset, True)


class FullNameColumn(Column):
    def render_footer(self, bound_column, table):
        return 'Employees#'


class DepartmentColumn(Column):
    def render_footer(self, bound_column, table):
        q = table.data.data
        return len(q) + 1


class EmployeeTable(tables.Table):
    class Meta:
        model = Employee
        fields = ['title', 'full_name', 'department', 'user__email', 'roles', ]
        order_by = ['full_name']
        template_name = 'entities/table-employee-model.html'
        attrs = {"class": "lcars-table lcars-golden-tanoi-color special-caption"}
        empty_text = 'No employee yet. Click Add to create one'
        per_page = 10

    caption = 'EMPLOYEES'

    full_name = FullNameColumn()
    department = DepartmentColumn()
    roles = TemplateColumn(
        template_name="entities/includes/_roles_cell.html",
        verbose_name="Roles",
        orderable=False,
    )
    buttons = TemplateColumn(
        template_name="entities/includes/_employee_actions_buttons.html",
        verbose_name="Actions",
        orderable=False,
    )

    def order_full_name(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "user__last_name")
        return queryset, True

