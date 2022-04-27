# youbee_main/users/views.py

# System libraries

# Third-party libraries
from allauth.account.adapter import get_adapter
from allauth.account.views import SignupView, LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetFromKeyView, PasswordResetFromKeyDoneView, PasswordChangeView

# Django modules
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

# Django apps
from users.roles import ENTITY_SUPERVISOR
from users.mixins import DisplayMessagesFromFormMixin

# Current app modules
from.forms import RegisterForm, MyResetPasswordForm, UserDetailForm


class RegisterView(DisplayMessagesFromFormMixin, SignupView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    success_url = '/'

    ctrl_flag = None

    def post(self, request, *args, **kwargs):
        self.ctrl_flag = request.POST.get('ctrl_flag')
        return super().post(self, request, args, kwargs)

    def form_valid(self, form):
        g = Group.objects.filter(name__exact=ENTITY_SUPERVISOR)

        if not g.exists():
            get_adapter(self.request).add_message(self.request,
                                                  messages.ERROR,
                                                  "account/messages/no_supervisor_permissions.txt")
            return HttpResponseRedirect(reverse('home'))
        else:
            return super().form_valid(form)

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)

        form.errors.clear()
        form.initial = form.cleaned_data

        return super().form_invalid(form)


class SigninView(DisplayMessagesFromFormMixin, LoginView):
    template_name = 'users/login.html'
    success_url = '/'

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)

        return HttpResponseRedirect(self.get_success_url())


class SignoutView(LogoutView):
    template_name = "users/logout.html"


class MyPasswordResetView(DisplayMessagesFromFormMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    form_class = MyResetPasswordForm
    success_url = reverse_lazy('users:password_reset_done')

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)

        return HttpResponseRedirect('/')


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class MyPasswordResetFromKeyView(DisplayMessagesFromFormMixin, PasswordResetFromKeyView):
    template_name = 'users/password_reset_from_key.html'
    success_url = reverse_lazy('users:reset_password_from_key_done')

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)
        return HttpResponseRedirect('/')

    def get_context_data(self, **kwargs):
        ret = super(PasswordResetFromKeyView, self).get_context_data(**kwargs)
        ret["action_url"] = reverse("users:reset_password_from_key", kwargs={"uidb36": self.kwargs["uidb36"],
                                                                             "key": self.kwargs["key"], }, )
        return ret


class MyPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    template_name = 'users/password_reset_from_key_done.html'


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = '/'


class UserDetailView(DisplayMessagesFromFormMixin, FormView):
    template_name = 'users/user_detail_form.html'
    form_class = UserDetailForm
    success_url = '/'

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        self.display_error_messages(self.request, form)
        return super().form_invalid(form)

    def get_initial(self):
        return {'title': self.request.user.employee.title,
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email1': self.request.user.email,
                'email2': self.request.user.employee.email2,
                'phone1': self.request.user.employee.phone1,
                'phone2': self.request.user.employee.phone2,
                'whatsapp': self.request.user.employee.whatsapp,
                'twitter': self.request.user.employee.twitter,
                }
