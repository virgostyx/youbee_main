# youbee_main/entities/fixtures.py

# System libraries
from sys import stdout

# Third-party libraries
from faker import Faker
from allauth.account.models import EmailAddress

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

# Django apps
from entities.models import Entity, EntityDetail, Department, Employee
from users.roles import ENTITY_SUPERVISOR, ENTITY_MANAGER, EMPLOYEE, create_roles
from users.fixtures import user_fixtures

# Current app modules


SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3
TEST_PASSWORD = 'test_pa22word'


class EntityFixtures:

    def __init__(self):
        self.faker = Faker()
        Faker.seed(0)
        self.entity = None

    def fake_entity_data(self):
        user = {
            'email': 'test.youbee+supervisor@gmail.com',
            'first_name': self.faker.first_name_male(),
            'last_name': self.faker.last_name(),
            'password': TEST_PASSWORD,
        }

        employee = self.fake_employee_data(title='1', is_manager=True)

        entity_details = {
            'entity': '',
            'phone1': '+22376061612',
            'phone2': '+22376061614',
            'email1': self.faker.ascii_company_email(),
            'email2': self.faker.ascii_company_email(),
            'address1': self.faker.street_address(),
            'address2': self.faker.street_address(),
            'city': self.faker.city(),
            'country': self.faker.country_code(),
            'zip_code': self.faker.postcode(),
        }

        return {
            'entity_name': 'The Youbee Test Company',
            'user': user,
            'entity_details': entity_details,
            'employee': employee,
        }

    def fake_department_data(self, name):
        return {
            'name': name,
            'entity': self.entity,
        }

    def get_random_department(self):
        ld = Department.objects.filter(entity=self.entity).values_list('id', flat=True).order_by('id')
        return Department.objects.get(pk=self.faker.random_element(elements=tuple(ld)))

    def fake_employee_data(self, title='1', is_manager=False):
        return {
            'user': '',
            'title': title,
            'gender': 'M' if title == '1' else 'F',
            'email2': '',
            'phone1': self.faker.phone_number(),
            'phone2': self.faker.phone_number(),
            'whatsapp': self.faker.phone_number(),
            'twitter': '',
            'entity': '',
            'department': '',
            'is_manager': is_manager,
        }

    def fake_employee_as(self, title, role_name):
        g = Group.objects.get(name=role_name)
        employee = self.fake_employee_data(title=title,
                                           is_manager=(role_name == ENTITY_SUPERVISOR or role_name == ENTITY_MANAGER))
        employee['entity'] = self.entity
        employee['department'] = self.get_random_department()
        first_name = self.faker.first_name_male() if title == '1' else self.faker.first_name_female()
        last_name = self.faker.last_name()
        username = user_fixtures.get_username(first_name, last_name)
        email = f'test.youbee+{username}@gmail.com'
        employee['email2'] = f'test.youbee+{username}2@gmail.com'
        employee['twitter'] = '@' + str(username)

        user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': TEST_PASSWORD,
        }

        return {
            'employee': employee,
            'user': user,
            'permissions': g,
        }

    def get_random_employee(self):
        e_list = Employee.objects.filter(entity=self.entity).values_list('id', flat=True).order_by('id')
        return Employee.objects.get(pk=self.faker.random_element(elements=tuple(e_list)))

    def create_entity(self):
        g = Group.objects.get(name=ENTITY_SUPERVISOR)
        entity_data = self.fake_entity_data()
        self.entity = Entity.objects.create(name=entity_data['entity_name'])
        entity_details = entity_data['entity_details']
        entity_details['entity'] = self.entity
        EntityDetail.objects.create(**entity_details)

        self.create_departments()

        user = user_fixtures.create_user(data=entity_data['user'], group=g)

        entity_employee = entity_data['employee']
        entity_employee['user'] = user
        entity_employee['email2'] = 'test.youbee+supervisor2@gmail.com'
        entity_employee['entity'] = self.entity
        entity_employee['department'] = Department.objects.get(entity=entity_employee['entity'], name='Administration')
        Employee.objects.create(**entity_employee)

        return self.entity

    def create_departments(self):
        d_list = []
        Department.objects.filter(name='Any').delete()

        d = entity_fixtures.fake_department_data('Administration')
        Department.objects.create(**d)
        d_list.append(d)

        d = entity_fixtures.fake_department_data('Operations')
        Department.objects.create(**d)
        d_list.append(d)

        d = entity_fixtures.fake_department_data('Management')
        Department.objects.create(**d)
        d_list.append(d)

        d = entity_fixtures.fake_department_data('Finances')
        Department.objects.create(**d)
        d_list.append(d)

        return d_list

    def create_employee_as(self, role_name):
        e = entity_fixtures.fake_employee_as(title=self.faker.random_element(elements=['1', '2', '3']),
                                             role_name=role_name)
        user = user_fixtures.create_user(data=e['user'], group=e['permissions'])

        e['employee']['user'] = user
        return Employee.objects.create(**e['employee'])

    def create_employees(self, verbosity=NORMAL, count=30):
        e_list = []
        # 1 Company Manager
        e = self.create_employee_as(ENTITY_MANAGER)
        e_list.append(e)

        # a few employees
        for i in range(count):
            e = self.create_employee_as(EMPLOYEE)
            e_list.append(e)

            if verbosity >= NORMAL:
                print("Created employee {}: {} {}".format(i + 1, e.user.first_name, e.user.last_name))

        return e_list

    def create_test_data(self, verbosity=NORMAL):

        # if verbosity >= NORMAL:
        #     stdout.write("=== Creating user roles ===\n")
        # create_roles(verbosity)

        # if verbosity >= NORMAL:
        #     stdout.write("=== Creating superuser ===\n")
        # user_fixtures.create_superuser()

        if verbosity >= NORMAL:
            stdout.write("=== Creating Entity ===\n")
        self.create_entity()

        if verbosity >= NORMAL:
            stdout.write("=== Creating Employees ===\n")
        self.create_employees(verbosity)


entity_fixtures = EntityFixtures()
