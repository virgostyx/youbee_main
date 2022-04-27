# project_name/app_module/file_name.py

# System libraries

# Third-party libraries

# Django modules

# Django apps
from users.models import Group

#  Current app modules


class ContextListsMixin:

    def _get_department_list(self, request):
        d_list = request.user.entity.departments.all()
        return d_list

    def _get_role_list(self):
        r_list = Group.objects.all()
        return r_list

