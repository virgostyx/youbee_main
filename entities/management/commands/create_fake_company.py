# entities/management/commands/create_fake_company.py

# System libraries


# Third-party libraries
from faker import Faker
from allauth.account.models import EmailAddress

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


# Django apps
from entities.models import Entity, EntityDetail, Department, Employee
from users.models import User
from users.roles import ENTITY_SUPERVISOR, ENTITY_MANAGER, EMPLOYEE


# Current app modules


SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3
TEST_PASSWORD = 'test_pa22word'


class Command(BaseCommand):
    help = "Create a fake company for testing purposes "
    faker = None
    entity = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker()
        Faker.seed(0)

    def add_arguments(self, parser):
        pass

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
            'phone1': self.faker.phone_number(),
            'phone2': self.faker.phone_number(),
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

    def get_fake_department(self):
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

# TODO: Replace by new function from allauth
    def get_username(self, first_name, last_name):
        return last_name[:5].lower() + first_name[:2].lower()

    def fake_employee_as(self, title, role_name):
        g = Group.objects.get(name__exact=role_name)
        employee = self.fake_employee_data(title=title,
                                      is_manager=(role_name == ENTITY_SUPERVISOR or role_name == ENTITY_MANAGER))
        employee['entity'] = self.entity
        employee['department'] = self.get_fake_department()
        first_name = self.faker.first_name_male() if title == '1' else self.faker.first_name_female()
        last_name = self.faker.last_name()
        username = self.get_username(first_name, last_name)
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

    def get_employee(self):
        e_list = Employee.objects.filter(entity=self.entity).values_list('id', flat=True).order_by('id')
        return Employee.objects.get(pk=self.faker.random_element(elements=tuple(e_list)))

    def create_entity(self):
        g = Group.objects.get(name__exact=ENTITY_SUPERVISOR)
        entity_data = self.fake_entity_data()
        self.entity = Entity.objects.create(name=entity_data['entity_name'])
        entity_details = entity_data['entity_details']
        entity_details['entity'] = self.entity
        EntityDetail.objects.create(**entity_details)
        self.create_departments()

        user = User.objects.create_user(**entity_data['user'])
        user.username = self.get_username(user.first_name, user.last_name)
        user.groups.add(g)
        user.save()

        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        entity_employee = entity_data['employee']
        entity_employee['user'] = user
        entity_employee['email2'] = 'test.youbee+supervisor2@gmail.com'
        entity_employee['entity'] = self.entity
        entity_employee['department'] = Department.objects.get(entity=entity_employee['entity'], name='Administration')
        Employee.objects.create(**entity_employee)

        return self.entity

    def create_departments(self):
        Department.objects.filter(name='Any').delete()

        d = self.fake_department_data('Administration')
        Department.objects.create(**d)

        d = self.fake_department_data('Operations')
        Department.objects.create(**d)

        d = self.fake_department_data('Management')
        Department.objects.create(**d)

        d = self.fake_department_data('Finances')
        Department.objects.create(**d)

        return

    def create_employee_as(self, role_name):
        e = self.fake_employee_as(title=self.faker.random_element(elements=['1', '2', '3']),
                                  role_name=role_name)
        # TODO: Use allauth functions
        user = User.objects.create_user(email=e['user']['email'], password=e['user']['password'])
        user.first_name = e['user']['first_name']
        user.last_name = e['user']['last_name']
        user.username = self.get_username(user.first_name, user.last_name)
        user.groups.add(e['permissions'])
        user.save()

        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        e['employee']['user'] = user
        return Employee.objects.create(**e['employee'])

    def create_employees(self):
        # 1 Company Manager
        e = self.create_employee_as(ENTITY_MANAGER)

        # a few employees
        for i in range(30):
            e = self.create_employee_as(EMPLOYEE)
            print("Created employee {}: {} {}".format(i+1, e.user.first_name, e.user.last_name))

        return

    def handle(self, *args, **options):

        verbosity = options.get("verbosity", NORMAL)

        if verbosity >= NORMAL:
            self.stdout.write("=== Creating the fake entity ===")

        # Do the job
        self.stdout.write("=== Creating Entity ===")
        self.create_entity()
        self.stdout.write("=== Creating Employees ===")
        self.create_employees()

        if verbosity >= NORMAL:
            self.stdout.write("=== Done ===")
