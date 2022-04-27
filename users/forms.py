# youbee_main/users/forms.py

# System libraries


# Third-party libraries
from allauth.account.forms import SignupForm, default_token_generator, ResetPasswordForm
from allauth.account.adapter import get_adapter
from allauth.utils import build_absolute_uri
from allauth.account.utils import user_pk_to_url_str
from phonenumber_field.formfields import PhoneNumberField

# Django modules
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

# Django apps
from users.roles import ENTITY_SUPERVISOR
from entities.models import Entity, EntityDetail, Department, Employee

# Current app modules


class RegisterForm(SignupForm):
    entity = forms.CharField(label="Entity* : ", help_text="Enter your entity name", max_length=48)
    title = forms.CharField(max_length=1)
    first_name = forms.CharField(label="First Name*: ", label_suffix="*", help_text="Enter your first name", max_length=150)
    last_name = forms.CharField(label="Last Name*: ", label_suffix="*", help_text="Enter your Last name", max_length=150)

    error_messages = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail* : '
        self.fields['password1'].label = 'Password*: '
        self.fields['password2'].label = 'Password again*: '

    def clean_entity(self):
        entity = self.cleaned_data['entity']

        if Entity.objects.filter(name__exact=entity).exists():
            self.add_error('entity', 'Entity exists already')
            # self.error_messages['entity'] = 'Entity exists already'
            # raise ValidationError(self.error_messages['entity'], code='entity')

        return entity

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()

    def save(self, request):
        user = super().save(request)
        g = Group.objects.filter(name__exact=ENTITY_SUPERVISOR)
        user.groups.add(g.first())
        user.save()

        c = Entity.objects.create(name=self.cleaned_data['entity'], supervisor=user)
        EntityDetail.objects.create(entity=c)
        d = Department.objects.create(entity=c, name='Any')
        Employee.objects.create(entity=c,
                                user=user,
                                title=self.cleaned_data['title'],
                                gender=('M' if self.cleaned_data['title'] == '1' else 'F'),
                                department=d,
                                is_manager=True)
        return user


class MyResetPasswordForm(ResetPasswordForm):
    template_name = 'users/password_reset.html'

    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        if not self.users:
            self._send_unknown_account_mail(request, email)
        else:
            self._send_password_reset_mail(request, email, self.users, **kwargs)
        return email

    def _send_unknown_account_mail(self, request, email):
        signup_url = build_absolute_uri(request, reverse("users:register"))
        context = {
            "current_site": get_current_site(request),
            "email": email,
            "request": request,
            "signup_url": signup_url,
        }
        get_adapter(request).send_mail("account/email/unknown_account", email, context)

    def _send_password_reset_mail(self, request, email, users, **kwargs):
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            path = reverse(
                "users:reset_password_from_key",
                kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key),
            )
            url = build_absolute_uri(request, path)

            context = {
                "current_site": get_current_site(request),
                "user": user,
                "password_reset_url": url,
                "request": request,
            }

            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )


class UserDetailForm(forms.Form):
    title = forms.CharField(max_length=1)
    first_name = forms.CharField(label="FIRST NAME*:",
                                 label_suffix="*",
                                 help_text="Enter your first name",
                                 max_length=150)
    last_name = forms.CharField(label="LAST NAME*:",
                                label_suffix="*",
                                help_text="Enter your last name", max_length=150)
    email1 = forms.EmailField(label='EMAIL*:', help_text='Enter email address', required=False)
    email2 = forms.EmailField(label='EMAIL2:', help_text='Enter another email address', required=False)
    phone1 = PhoneNumberField(label='PHONE1:', required=False)
    phone2 = PhoneNumberField(label='PHONE2:', required=False)
    whatsapp = PhoneNumberField(label='WHATSAPP:', required=False)
    twitter = forms.CharField(label='TWITTER:', max_length=15, required=False)

    def save(self, request):
        if self.has_changed():
            user = request.user

            user.employee.title = self.cleaned_data['title']
            user.employee.email2 = self.cleaned_data['email2']
            user.employee.phone1 = self.cleaned_data['phone1']
            user.employee.phone2 = self.cleaned_data['phone2']
            user.employee.whatsapp = self.cleaned_data['whatsapp']
            user.employee.twitter = self.cleaned_data['twitter']
            user.employee.save()

            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
            messages.success(request, "User detail has been saved")
        else:
            messages.info(request, "User detail has not been changed")
