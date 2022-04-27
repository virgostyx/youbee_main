# youbee_main/users/models.py

# System libraries
import json

# Third-party libraries


# Django modules
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models

# Django apps

# Current-app modules
from .roles import ROLES, ENTITY_SUPERVISOR_IDX, ENTITY_MANAGER_IDX, EMPLOYEE_IDX


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField('username', max_length=150, blank=True)
    email = models.EmailField('email', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        constraints = [models.UniqueConstraint(fields=['email'], name='Unique Email Address')]
        ordering = ['email']

    def add_role(self, role):
        return self.groups.add(Group.objects.get(name=role))

    def has_role(self, role):
        return self.groups.filter(name=role).exists()

    @property
    def get_roles_list(self):
        r_list = self.groups.all()
        return list(r_list.values_list('pk', flat=True))

    @property
    def get_roles_names(self):
        r_list = self.groups.all()
        return list(r_list.order_by('name').values_list('name', flat=True))

    @property
    def get_roles(self):
        return self.groups.all()

    @property
    def get_roles_list_tojson(self):
        return json.dumps(self.get_roles_list)

    @property
    def is_entity_supervisor(self):
        return self.has_role(ROLES[ENTITY_SUPERVISOR_IDX])

    @property
    def is_entity_manager(self):
        return self.has_role(ROLES[ENTITY_MANAGER_IDX])

    @property
    def is_employee(self):
        return self.has_role(ROLES[EMPLOYEE_IDX])




