# youbee_main/entities/views.py

# System libraries

# Third-party libraries
from django_tables2 import SingleTableView

# Django modules
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponseRedirect
from django.contrib import messages

# Django apps
from users.mixins import DisplayMessagesFromFormMixin

#  Current app modules
from .forms import EntityDetailForm, DepartmentCreateForm, DepartmentUpdateForm, EmployeeCreateForm, EmployeeUpdateForm
from .models import Department, Employee
from .tables import DepartmentTable, EmployeeTable
from .mixins import ContextListsMixin
from .utils import get_entity_from_user


class EntityDetailView(DisplayMessagesFromFormMixin, FormView):
    template_name = 'entities/entity_detail.html'
    form_class = EntityDetailForm
    success_url = '/'
    entity = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.entity = get_entity_from_user(request.user)

    def get_initial(self):
        ed = self.entity.entity_details
        return {
            'name': self.entity.name,
            'address1': ed.address1,
            'address2': ed.address2,
            'city': ed.city,
            'zip_code': ed.zip_code,
            'country': ed.country.code,
            'phone1': ed.phone1,
            'phone2': ed.phone2,
            'email1': ed.email1,
            'email2': ed.email2,
        }

    def form_valid(self, form):
        form.save(commit=False, request=self.request)
        messages.success(self.request, "Entity details have been saved")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)
        return super().form_invalid(form)


class DepartmentListView(ListView):
    model = Department
    template_name = 'entities/department_list.html'
    context_object_name = 'department_list'
    paginate_by = 10

    def get_queryset(self):
        e = get_entity_from_user(self.request.user)
        return e.departments.all()


class CreateDepartmentView(DisplayMessagesFromFormMixin, CreateView):
    model = Department
    template_name = 'entities/department_form.html'
    form_class = DepartmentCreateForm
    success_url = reverse_lazy('entities:entity_departments')
    context_object_name = 'department'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'request': self.request,
            }
        )

        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "New Department has been saved")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)
        return super().form_invalid(form)


class UpdateDepartmentView(DisplayMessagesFromFormMixin, UpdateView):
    model = Department
    template_name = 'entities/department_update_form.html'
    form_class = DepartmentUpdateForm
    success_url = reverse_lazy('entities:entity_departments')
    context_object_name = 'department'

    def form_valid(self, form):
        messages.success(self.request, "New Department has been saved")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)
        return super().form_invalid(form)


class DeleteDepartmentView(DeleteView):
    model = Department
    template_name = 'entities/department_confirm_delete.html'
    context_object_name = 'department'
    success_url = reverse_lazy('entities:entity_departments')


class EmployeeListView(ListView):
    model = Employee
    template_name = 'entities/employee_list.html'
    context_object_name = 'employee_list'
    paginate_by = 10

    def get_queryset(self):
        e = get_entity_from_user(self.request.user)
        q = e.employees.all()
        print(q)
        return q.order_by('user__last_name')


class CreateEmployeeView(ContextListsMixin, DisplayMessagesFromFormMixin, FormView):
    template_name = 'entities/employee_form.html'
    form_class = EmployeeCreateForm
    success_url = reverse_lazy('entities:entity_employees')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.extra_context = {'department_list': self._get_department_list(self.request),
                              'role_list': self._get_role_list(),
                              }

    def form_valid(self, form):
        d = form.save()
        messages.success(self.request, "New employee has been saved")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        self.display_error_messages(self.request, form)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'request': self.request,
            }
        )

        return kwargs


class UpdateEmployeeView(ContextListsMixin, UpdateView):
    model = Employee
    template_name = 'entities/employee_update_form.html'
    form_class = EmployeeUpdateForm
    context_object_name = 'employee'
    success_url = reverse_lazy('entities:entity_employees')

    def form_valid(self, form):
        self.object = form.save(record=self.object)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.extra_context = {'department_list': self._get_department_list(self.request),
                              'role_list': self._get_role_list(),
                              }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'request': self.request,
            }
        )

        return kwargs


class DeleteEmployeeView(DeleteView):
    model = Employee
    template_name = 'entities/employee_confirm_delete.html'
    context_object_name = 'employee'
    success_url = reverse_lazy('entities:entity_employees')


class DepartmentTableView(SingleTableView):
    model = Department
    table_class = DepartmentTable
    template_name = 'entities/department_table.html'

    def get_queryset(self):
        e = get_entity_from_user(self.request.user)
        q = e.departments.all()
        return q


class EmployeeTableView(SingleTableView):
    model = Employee
    table_class = EmployeeTable
    template_name = 'entities/employee_table.html'

    def get_queryset(self):
        e = get_entity_from_user(self.request.user)
        q = Employee.objects.filter(entity=e).exclude(user=self.request.user)
        return q.order_by('user__last_name')
