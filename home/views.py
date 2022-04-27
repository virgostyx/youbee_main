# youbee_main/home/views.py

# System libraries


# Third-party libraries
from allauth.account.adapter import get_adapter
from django_tables2 import MultiTableMixin

# Django modules
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.sites.shortcuts import get_current_site

# Django apps
from entities.utils import get_entity_from_user
from entities.models import Employee

# Current app modules
from .forms import ContactForm
from .tables import DepartmentDashboardTable, EmployeeDashboardTable


class HomePageView(TemplateView):
    template_name = "home/home.html"


class AboutPageView(TemplateView):
    template_name = "home/about.html"


class ContactPageView(FormView):
    template_name = "home/contact.html"
    form_class = ContactForm
    success_url = '/'

    def get_initial(self):
        if self.request.user.is_authenticated:
            self.initial = {"email": self.request.user.email,
                            "firstname": self.request.user.first_name,
                            "lastname": self.request.user.last_name,
                            }
        return super().get_initial()

    def form_valid(self, form):
        email = self.request.POST.get('email')
        copy_to_self = self.request.POST.get('copy_to_self')

        context = {
            'current_site': get_current_site(self.request),
            'email': email,
            'first_name': self.request.POST.get('firstname'),
            'last_name': self.request.POST.get('lastname'),
            'subject': self.request.POST.get('subject'),
            'message': self.request.POST.get('message'),
        }

        msg = get_adapter(self.request).render_mail(
            template_prefix='home/email/contact_request',
            email=email,
            context=context
        )

        if copy_to_self:
            msg.from_email = msg.to[0]  # The sender is the same as the receiver
            msg.send()

        msg.from_email, msg.to = msg.to[0], [msg.from_email]  # this is correction of render_mail which is foreseen to
        # send a message to a user from the webmaster. We need to swap the sender and the receiver since we need to send
        # a message from the user to the webmaster
        msg.send()

        return super().form_valid(form)


class DashboardPageView(MultiTableMixin, TemplateView):
    template_name = 'home/dashboard.html'
    tables = [
        DepartmentDashboardTable,
        EmployeeDashboardTable,
    ]

    def get_tables_data(self):
        e = get_entity_from_user(self.request.user)
        q1 = e.departments.all()
        q2 = Employee.objects.filter(entity=e).exclude(user=self.request.user).order_by('user__last_name')
        self.tables_data = [q1, q2]

        return self.tables_data
