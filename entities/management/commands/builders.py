# project_name/app_module/file_name.py

# System libraries

# Third-party libraries
from phone_gen import PhoneNumber
from allauth.account.models import EmailAddress

# Django modules
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

# Django apps
from entities.models import Entity, EntityDetail, Department, Employee
from users.models import User
from users.roles import EMPLOYEE, ENTITY_SUPERVISOR, ENTITY_MANAGER

#  Current app modules
from .base_builder import BaseFakeDataBuilder, BaseEntityBuilder
from .constants import DEPARTMENT_COUNT, MANAGER_COUNT, EMPLOYEE_COUNT, EMAIL_PREFIX, EMAIL_SUFFIX, \
    SUPERVISOR_DEPARTMENT, DEPARTMENT_LIST, TEST_PASSWORD, VALID_TITLES, SUPERVISOR_EMAIL


class EntityBuilder(BaseFakeDataBuilder):
    def __init__(self):
        super().__init__()
        self.entity = None
        self.entity_name = None
        self.entity_supervisor_email = None

        self.d_builder = DepartmentBuilder(self)
        self.m_builder = ManagerBuilder(self)
        self.e_builder = EmployeeBuilder(self)

        self.department_count = DEPARTMENT_COUNT
        self.manager_count = MANAGER_COUNT
        self.employee_count = EMPLOYEE_COUNT

        self.set_entity_name()
        self.set_entity_supervisor_email()

        return

    def set_entity_name(self, name=None):
        new_name = self.faker.company() if name is None else name

        while Entity.objects.filter(name__iexact=new_name).exists():
            new_name = self.faker.company()

        self.entity_name = new_name

        return self.entity_name

    def set_entity_supervisor_email(self, email=None):
        if email is not None:
            if User.objects.filter(email__iexact=email).exists():
                raise Exception
            else:
                self.entity_supervisor_email = email

        return self.entity_supervisor_email

    def set_department_count(self, count=DEPARTMENT_COUNT):
        self.department_count = count if 1 < count <= len(DEPARTMENT_LIST) else DEPARTMENT_COUNT
        return self.department_count

    def set_employee_count(self, count=EMPLOYEE_COUNT):
        self.employee_count = count if count > 0 else EMPLOYEE_COUNT
        return self.employee_count

    def set_manager_count(self, count=MANAGER_COUNT):
        self.manager_count = count if count > 0 else MANAGER_COUNT
        return self.manager_count

    def fake_entity_data(self):
        country_code = self.faker.country_code()
        phone_number = PhoneNumber(country_code)
        entity_details = {
            'entity': '',
            'phone1': phone_number.get_number(),
            'phone2': phone_number.get_number(),
            'email1': self.faker.ascii_company_email(),
            'email2': self.faker.ascii_company_email(),
            'address1': self.faker.street_address(),
            'address2': self.faker.street_address(),
            'city': self.faker.city(),
            'country': country_code,
            'zip_code': self.faker.postcode(),
        }

        return {
            'entity_name': self.entity_name,
            'entity_details': entity_details,
        }

    def get_random_department(self):
        if self.entity is None:
            raise Exception('There is no entity built')

        if self.entity.departments.count == 0:
            raise Exception('There is no department built')

        ld = Department.objects.filter(entity=self.entity).values_list('id', flat=True).order_by('id')
        return Department.objects.get(pk=self.faker.random_element(elements=tuple(ld)))

    def get_random_employee(self):
        if self.entity is None:
            raise Exception('There is no entity built')

        if self.entity.employee.count == 0:
            raise Exception('There is no employee built')

        e_list = Employee.objects.filter(entity=self.entity).values_list('id', flat=True).order_by('id')
        return Employee.objects.get(pk=self.faker.random_element(elements=tuple(e_list)))

    def build_entity(self):
        entity_data = self.fake_entity_data()
        self.entity = Entity.objects.create(name=entity_data['entity_name'])
        entity_details = entity_data['entity_details']
        entity_details['entity'] = self.entity
        EntityDetail.objects.create(**entity_details)

        return self.entity

    def build_departments(self):
        self.d_builder.set_entity_builder(self)
        return self.d_builder.build()

    def build_supervisor(self):
        u = self.e_builder.build_supervisor(self.entity_supervisor_email)
        self.entity.supervisor = u
        self.entity.save()
        entity_employee = EmployeeBuilder().fake_employee_data(is_manager=True)
        entity_employee['user'] = u
        entity_employee['email2'] = self.faker.ascii_free_email()
        entity_employee['entity'] = self.entity
        entity_employee['twitter'] = '@' + str(u.username)
        entity_employee['department'] = Department.objects.get(entity=entity_employee['entity'],
                                                               name=SUPERVISOR_DEPARTMENT)

        return Employee.objects.create(**entity_employee)

    def build_managers(self):
        return self.m_builder.build()

    def build_employees(self):
        return self.e_builder.build()

    def build(self):
        e = self.build_entity()
        self.build_departments()
        self.build_supervisor()
        self.build_managers()
        self.build_employees()
        return e


class DepartmentBuilder(BaseEntityBuilder):
    def build(self):
        d_list = []

        if self.entity_builder.entity:
            d_count = self.entity_builder.department_count \
                if self.entity_builder.department_count <= len(DEPARTMENT_LIST) \
                else len(DEPARTMENT_LIST)

            Department.objects.filter(name='Any').delete()

            data = {'name': SUPERVISOR_DEPARTMENT,
                    'entity': self.entity_builder.entity,
                    }

            d = Department.objects.create(**data)
            d_list.append(d.name)

            if d_count > 0:
                for i in range(d_count):
                    data['name'] = DEPARTMENT_LIST[i]
                    d = Department.objects.create(**data)
                    d_list.append(d.name)

        return d_list


class UserBuilder(BaseEntityBuilder):
    def get_username(self, title='1'):
        if title not in VALID_TITLES:
            raise ValueError("Invalid title %s: must be '1', '2' or '3'" % title)

        first_name = self.faker.first_name_male() if title == '1' else self.faker.first_name_female()
        last_name = self.faker.last_name()
        username = last_name[:5].lower() + first_name[:2].lower()
        return first_name, last_name, username

    def fake_user_unique_email(self, title='1'):
        first_name, last_name, username = self.get_username(title)
        email = EMAIL_PREFIX + username + EMAIL_SUFFIX

        while User.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name).exists() \
                or \
                User.objects.filter(email__iexact=email).exists():
            first_name, last_name, username = self.get_username(title)
            email = EMAIL_PREFIX + username + EMAIL_SUFFIX

        return first_name, last_name, username, email

    def fake_user(self, email=None, title='1'):
        if email is None or User.objects.filter(email=email).exists():
            first_name, last_name, username, email = self.fake_user_unique_email(title=title)
        else:
            first_name, last_name, username = self.get_username(title=title)

        user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': TEST_PASSWORD,
            'group': '',
        }
        return user

    def fake_user_as(self, title='1', email=None, role=EMPLOYEE):
        u = self.fake_user(email=email, title=title)

        try:
            g = Group.objects.get(name=role)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('The role %s does not exist' % role)
        else:
            u['group'] = g

        return u

    def fake_supervisor(self, email=None):
        return self.fake_user_as(email=email, role=ENTITY_SUPERVISOR)

    def build_user(self, email=None, role=EMPLOYEE):
        data = self.fake_user_as(email=email, role=role)

        return self.build_user_from(data)

    @staticmethod
    def build_user_from(data):
        u = User.objects.create_user(email=data['email'], password=data['password'])
        u.first_name = data['first_name']
        u.last_name = data['last_name']
        u.username = data['username']
        u.save()

        if data['group']:
            u.groups.add(data['group'])

        EmailAddress.objects.create(user=u, email=u.email, verified=True, primary=True)

        return u

    def build_supervisor(self, email=None):
        return self.build_user(email=email, role=ENTITY_SUPERVISOR)

    def build(self):
        return self.build_user()


class EmployeeBuilder(UserBuilder):
    def fake_employee_data(self, title='1', is_manager=False):
        if title not in VALID_TITLES:
            raise ValueError("Invalid title %s: must be '1', '2' or '3'" % title)

        phone_number = PhoneNumber(self.faker.country_code())

        return {
            'user': '',
            'title': title,
            'gender': '',
            'email2': self.faker.ascii_free_email(),
            'phone1': phone_number.get_number(),
            'phone2': phone_number.get_number(),
            'whatsapp': phone_number.get_number(),
            'twitter': '',
            'entity': '',
            'department': '',
            'is_manager': is_manager,
        }

    def fake_employee_as(self, title, role_name):
        u = self.fake_user_as(title=title, role=role_name)
        employee = self.fake_employee_data(title=title,
                                           is_manager=(role_name == ENTITY_SUPERVISOR or role_name == ENTITY_MANAGER))
        employee['entity'] = self.entity_builder.entity
        employee['department'] = self.entity_builder.get_random_department()
        employee['twitter'] = '@' + str(u['username'])
        employee['user'] = u

        return employee

    def create_employee_as(self, role_name=EMPLOYEE):
        title = self.faker.random_element(elements=['1', '2', '3'])
        e = self.fake_employee_as(title=title,
                                  role_name=role_name)
        e['user'] = self.build_user_from(data=e['user'])

        return Employee.objects.create(**e)

    def build(self):
        e_list = []

        if self.entity_builder.entity:
            for _ in range(self.entity_builder.employee_count):
                e = self.create_employee_as(EMPLOYEE)
                e_list.append(e.pk)

        return e_list


class ManagerBuilder(EmployeeBuilder):
    def build(self):
        m_list = []

        if self.entity_builder.entity:
            for _ in range(self.entity_builder.manager_count):
                e = self.create_employee_as(ENTITY_MANAGER)
                m_list.append(e.pk)

        return m_list


class DatabaseEngineer:
    def __init__(self):
        self.builder = None

    def construct_entity(self,
                         entity_name=None,
                         supervisor_email=None,
                         department_count=None,
                         manager_count=None,
                         employee_count=None):

        self.builder = EntityBuilder()

        if entity_name is not None:
            self.builder.set_entity_name(entity_name)

        if supervisor_email is not None:
            self.builder.set_entity_supervisor_email(supervisor_email)

        if department_count is not None:
            self.builder.set_department_count(department_count)

        if manager_count is not None:
            self.builder.set_manager_count(manager_count)

        if employee_count is not None:
            self.builder.set_employee_count(employee_count)

        return self.builder.build()

    @property
    def entity(self):
        return self.builder.entity
