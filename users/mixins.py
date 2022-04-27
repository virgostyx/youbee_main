# project_name/app_module/file_name.py

# System libraries

# Third-party libraries

# Django modules
from django.contrib import messages

# Django apps

#  Current app modules


class DisplayMessagesFromFormMixin(object):
    def display_error_messages(self, request, form):
        for f, errors in form.errors.items():
            for e in errors:
                messages.error(request, "{}: {}".format('all' if f == '__all__' else f, e))
        return
