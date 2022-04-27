# youbee_main/entities/models.py

# System libraries
from enum import Enum

# Third-party libraries
from model_utils.fields import StatusField, MonitorField
from model_utils import Choices
from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

# Django modules
from django.db import models
from django.urls import reverse

# Django apps
from users.models import User

#  Current app modules


def _employee_slug_fields(instance):
    return "{0}-{1}".format(instance.user.first_name, instance.user.last_name)


class Entity(models.Model):
    class Meta:
        verbose_name_plural = 'entities'
        constraints = [models.UniqueConstraint(fields=['name'], name='unique_entity_name')]
        ordering = ['name']

    name = models.CharField(max_length=48,
                            verbose_name='Name',
                            unique=True,
                            help_text='Name of the entity you are working for. Please make sure it is correct')
    slug_name = AutoSlugField(populate_from='name',
                              verbose_name='Slug',
                              max_length=54,
                              unique=True,
                              editable=False)
    supervisor = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    parent = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='partners')

    def __str__(self):
        return "{name}".format(name=self.name)

    @property
    def get_absolute_url(self):
        return reverse('entities:entity_detail')


class EntityDetail(models.Model):
    class Meta:
        verbose_name_plural = 'entity_details'

    entity = models.OneToOneField(Entity,
                                  on_delete=models.CASCADE,
                                  related_name='entity_details')

    phone1 = PhoneNumberField(blank=True,
                              verbose_name='Phone1',
                              help_text="Enter a phone number")
    phone2 = PhoneNumberField(blank=True,
                              verbose_name='Phone2',
                              help_text="Enter a phone number")

    email1 = models.EmailField(max_length=48,
                               verbose_name='Email1',
                               blank=True,
                               help_text="Enter an email address")
    email1_checked = models.BooleanField(default=False, editable=False)
    email2 = models.EmailField(max_length=48,
                               verbose_name = 'Email2',
                               blank=True,
                               help_text="Enter an email address")
    email2_checked = models.BooleanField(default=False, editable=False)

    address1 = models.CharField(max_length=128,
                                verbose_name='Address1',
                                blank=True,
                                help_text="Enter an address")
    address2 = models.CharField(max_length=128,
                                verbose_name='Address2',
                                blank=True,
                                help_text="Enter an address")
    city = models.CharField(max_length=32,
                            verbose_name='City',
                            blank=True,
                            help_text="Enter a city")
    country = CountryField(blank_label='(select country)',
                           verbose_name='Country',
                           blank=True)
    zip_code = models.CharField(max_length=16,
                                verbose_name='Zip Code',
                                blank=True,
                                help_text="Enter a zip code")

    def __str__(self):
        return "{name} - [phone: {phone} email: {email}]".format(
            name=self.entity.name, phone=self.phone1,
            email=self.email1)

    @property
    def get_values(self):
        return {'entity': self.entity,
                'name': self.entity.name,
                'address1': self.address1,
                'address2': self.address2,
                'city': self.city,
                'country': self.country,
                'zip_code': self.zip_code,
                'email1': self.email1,
                'email2': self.email2,
                'phone1': self.phone1,
                'phone2': self.phone2,
                }

    @property
    def get_absolute_url(self):
        return reverse('entities:entity_detail')


class Department(models.Model):
    class Meta:
        permissions = [('unlink_department', 'Can unlink department'), ]
        unique_together = [['entity', 'name'], ]
        ordering = ['entity', 'name']

    name = models.CharField(max_length=24,
                            verbose_name='Name',
                            help_text='Enter a department name')
    entity = models.ForeignKey(Entity,
                               on_delete=models.CASCADE,
                               related_name='departments')

    @property
    def get_values(self):
        return {
            'name': self.name,
            'entity': self.entity,
        }

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        return self.employees.count()


class Employee(models.Model):
    class Meta:
        permissions = [('unlink_employee', 'Can unlink employee'), ]
        ordering = ['user__last_name', 'user__first_name']

    class GENDERS(Enum):
        male = ('M', 'Male')
        female = ('F', 'Female')
        undefined = ('U', 'Undefined')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    class TITLES(Enum):
        mr = ('1', 'Mr')
        mrs = ('2', 'Mrs')
        ms = ('3', 'Ms')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    STATUS = Choices('not sent', 'initiated', 'sent',
                     'confirmed OK', 'confirmed not OK')

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    slug_name = AutoSlugField(
        populate_from=_employee_slug_fields,
        max_length=200,
        unique=True,
        editable=False)
    title = models.CharField(max_length=1,
                             default='1',
                             choices=[x.value for x in TITLES],
                             help_text='Select a title in the list.')
    gender = models.CharField(max_length=1,
                              default='U',
                              choices=[x.value for x in GENDERS])

    email2 = models.EmailField(max_length=48,
                               blank=True)
    phone1 = PhoneNumberField(blank=True)
    phone2 = PhoneNumberField(blank=True)
    whatsapp = PhoneNumberField(blank=True,
                                help_text='Enter a whatsapp number')
    twitter = models.CharField(max_length=15,
                               blank=True,
                               help_text='Enter a Twitter account')
    # Status data
    status = StatusField(default='not sent',
                         choices_name='STATUS', editable=False)
    status_changed = MonitorField(monitor='status', editable=False)
    initiated_on = MonitorField(monitor='status', when=[
        'initiated'], editable=False)
    sent_on = MonitorField(monitor='status', when=['sent'], editable=False)
    confirmed_on = MonitorField(monitor='status', when=[
        'confirmed OK', 'confirmed not OK'], editable=False)

    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, editable=False, related_name='employees')
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, editable=False, related_name='employees')
    is_manager = models.BooleanField(default=False, editable=False)

    @property
    def full_name(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        self.gender = 'M' if self.title == '1' else 'F'
        self.is_manager = (self.user.is_entity_supervisor or self.user.is_entity_manager)
        super().save(*args, **kwargs)
        return self

    def __str__(self):
        return "{first_name} {last_name}".format(first_name=self.user.first_name, last_name=self.user.last_name)


class Partnership(models.Model):
    class Meta:
        verbose_name_plural = 'partnerships'

    STATUS = Choices('not sent', 'sent', 'OK', 'NOK')

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    # Status data
    status = StatusField(default='not sent',
                         choices_name='STATUS',
                         editable=False)
    status_changed = MonitorField(monitor='status',
                                  editable=False)
    sent_on = MonitorField(monitor='status',
                           when=['sent'],
                           editable=False)
    confirmed_on = MonitorField(monitor='status',
                                when=['OK', 'NOK'],
                                editable=False)
    validity_start = models.DateField()
    validity_end = models.DateField()
