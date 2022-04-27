# youbee_main/entities/forms.py

# System libraries

# Third-party libraries
from phonenumber_field.formfields import PhoneNumberField

# Django modules
from django.forms import ModelForm, CharField, EmailField, ModelChoiceField
from django.forms.utils import ErrorList
from django.contrib.auth.models import Group

# Django apps
from users.models import User

#  Current app modules
from .models import EntityDetail, Entity, Department, Employee
from .utils import get_entity_from_user


class EntityDetailForm(ModelForm):
    class Meta:
        model = EntityDetail
        exclude = ['entity']

    name = CharField(label='Entity*:', max_length=48, help_text='Enter your entity name')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        self.fields['name'].value = self.initial['name']
        return

    def save(self, commit=False, request=None):
        e = get_entity_from_user(request.user)
        ed = e.entity_details

        if self.fields['name'].has_changed(self.initial['name'], self.cleaned_data['name']):
            e.name = self.cleaned_data['name']
            e.save()

        if self.has_changed():
            ed.address1 = self.cleaned_data['address1']
            ed.address2 = self.cleaned_data['address2']
            ed.city = self.cleaned_data['city']
            ed.zip_code = self.cleaned_data['zip_code']
            ed.country = self.cleaned_data['country']
            ed.phone1 = self.cleaned_data['phone1']
            ed.phone2 = self.cleaned_data['phone2']
            ed.email1 = self.cleaned_data['email1']
            ed.email2 = self.cleaned_data['email2']
            ed.save()

    def clean_name(self):
        entity_name = self.cleaned_data['name']

        if self.fields['name'].has_changed(self.initial['name'], entity_name):
            if Entity.objects.filter(name__exact=entity_name).exists():
                self.add_error('name', 'Entity does exist already')

        return entity_name


class DepartmentCreateForm(ModelForm):
    class Meta:
        model = Department
        exclude = ['entity']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request') if 'request' in kwargs else None
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'DEPARTMENT*:'

    def clean_name(self):
        d = self.cleaned_data['name']
        e = get_entity_from_user(self.request.user)

        if Department.objects.filter(name__iexact=d, entity=e).exists():
            self.add_error('name', 'Department does exist already')

        return d

    def save(self, commit=True):
        e = get_entity_from_user(self.request.user)
        return Department.objects.create(name=self.cleaned_data['name'], entity=e)


class DepartmentUpdateForm(ModelForm):
    class Meta:
        model = Department
        exclude = ['entity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'DEPARTMENT*:'

    def clean_name(self):
        d = self.cleaned_data['name']

        if self.fields['name'].has_changed(d, self.instance.name):
            if Department.objects.filter(name__iexact=d, entity=self.instance.entity).exists():
                self.add_error('name', 'Department does exist already')
        else:
            self.add_error('name', 'Data did not change')

        return d


class BaseEmployeeForm(ModelForm):
    class Meta:
        model = Employee
        exclude = ['entity', 'user', 'gender', 'is_manager']

    title = CharField(max_length=1, help_text='Select the title')
    first_name = CharField(max_length=150, label='FIRST NAME*:', help_text='Enter the first name')
    last_name = CharField(max_length=150, label='LAST NAME*:', help_text='Enter the last name')
    password = CharField(max_length=128, label='PASSWORD*:')
    role = ModelChoiceField(label='ROLE*:', required=True, queryset=Group.objects.all())
    email1 = EmailField(label='EMAIL*:', help_text='Enter email address')
    email2 = EmailField(label='EMAIL2:', help_text='Enter another email address', required=False)
    phone1 = PhoneNumberField(label='PHONE1:', required=False)
    phone2 = PhoneNumberField(label='PHONE2:', required=False)
    whatsapp = PhoneNumberField(label='WHATSAPP:', required=False)
    twitter = CharField(label='TWITTER:', max_length=15, required=False)
    department = ModelChoiceField(label='DEPARTMENT*:', required=True, queryset=None)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request') if 'request' in kwargs else None
        super().__init__(*args, **kwargs)

        if self.request:
            e = get_entity_from_user(self.request.user)
            self.fields['department'].queryset = e.departments.all()

    def clean_password(self):
        return self.cleaned_data['password'].strip()

    def clean_email2(self):
        return self.cleaned_data['email2'].strip()

    def clean_twitter(self):
        return self.cleaned_data['twitter'].strip().lower()


class EmployeeCreateForm(BaseEmployeeForm):
    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()

    def clean_email1(self):
        email1 = self.cleaned_data['email1'].strip()

        if User.objects.filter(email__iexact=email1).exists():
            self.add_error('email1', 'Employee does exist already')

        return email1

    def clean_password(self):
        p = super().clean_password()

        if p:
            return p
        else:
            self.add_error("password", "You must enter a password")

    def save(self, commit=True):
        # Create the new user
        u = User.objects.create_user(self.cleaned_data['email1'], self.cleaned_data['password'])
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.groups.add(self.cleaned_data['role'])
        u.save()

        # create the new employee
        e = Employee.objects.create(
            user=u,
            title=self.cleaned_data['title'],
            email2=self.cleaned_data['email2'],
            phone1=self.cleaned_data['phone1'],
            phone2=self.cleaned_data['phone2'],
            whatsapp=self.cleaned_data['whatsapp'],
            twitter=self.cleaned_data['twitter'],
            department=self.cleaned_data['department'],
            entity=get_entity_from_user(self.request.user)
        )

        return e


class EmployeeUpdateForm(BaseEmployeeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = 'PASSWORD:'
        self.fields['password'].required = False

    def save(self, commit=True, record=None):

        record.user.groups.clear()
        record.user.groups.add(self.cleaned_data['role'])
        p = self.cleaned_data['password']

        if p:
            record.user.set_password(p)

        record.user.save()

        # create the new employee
        record.title = self.cleaned_data['title']
        record.email2 = self.cleaned_data['email2']
        record.phone1 = self.cleaned_data['phone1']
        record.phone2 = self.cleaned_data['phone2']
        record.whatsapp = self.cleaned_data['whatsapp']
        record.twitter = self.cleaned_data['twitter']
        record.department = self.cleaned_data['department']
        record.save()

        return record
