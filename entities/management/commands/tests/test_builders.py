# youbee_main/fixtures/builders/tests/test_builders.py

# System libraries

# Third-party libraries
import pytest
from allauth.utils import email_address_exists

# Django modules
from django.core.exceptions import ObjectDoesNotExist

# Django apps
from users.models import User
from users.roles import EMPLOYEE, ENTITY_MANAGER
from entities.models import Employee, Entity

#  Current app modules
from ..constants import DEPARTMENT_COUNT, MANAGER_COUNT, EMPLOYEE_COUNT, SUPERVISOR_DEPARTMENT, EMAIL_PREFIX, \
    EMAIL_SUFFIX, TEST_PASSWORD, SUPERVISOR_EMAIL
from ..builders import EntityBuilder, UserBuilder, EmployeeBuilder, ManagerBuilder, DatabaseEngineer


class BaseTestBuilder:
    @pytest.fixture
    def eb(self, db):
        return EntityBuilder()

    @pytest.fixture
    def eb_with_roles(self, init_empty_db):
        return EntityBuilder()


class TestDepartmentBuilder(BaseTestBuilder):  # tests passed
    def test_build(self, eb):
        eb.build_entity()
        d_list = eb.build_departments()
        assert len(d_list) == 4
        assert SUPERVISOR_DEPARTMENT in d_list


class TestUserBuilder(BaseTestBuilder):  # tests passed
    @pytest.fixture
    def ub(self, eb):
        return UserBuilder(eb)

    @pytest.fixture
    def ub_with_roles(self, eb_with_roles):
        return UserBuilder(eb_with_roles)

    def test_get_username_default(self, ub):
        f, l, u = ub.get_username()
        assert f is not None
        assert l is not None
        assert u is not None

    def test_get_username_correct_title(self, ub):
        f, l, u = ub.get_username(title='2')
        assert f is not None
        assert l is not None
        assert u is not None

    def test_get_username_incorrect_title(self, ub):
        with pytest.raises(ValueError):
            ub.get_username(title='4')

    def test_fake_user_unique_email(self, ub):
        f, l, u, e = ub.fake_user_unique_email()
        assert f != ''
        assert l is not None
        assert u is not None
        assert e is not None
        assert e.startswith(EMAIL_PREFIX)
        assert e.endswith(EMAIL_SUFFIX)

    def test_fake_user_defaults(self, ub):
        data = ub.fake_user()
        assert data['email'] is not None
        assert data['first_name'] is not None
        assert data['last_name'] is not None
        assert data['username'] is not None
        assert data['password'] == TEST_PASSWORD

    def test_fake_user_with_email(self, ub):
        data = ub.fake_user(email=SUPERVISOR_EMAIL)
        assert data['email'] == SUPERVISOR_EMAIL
        assert data['first_name'] is not None
        assert data['last_name'] is not None
        assert data['username'] is not None
        assert data['password'] == TEST_PASSWORD

    def test_fake_user_as_defaults(self, ub_with_roles):
        data = ub_with_roles.fake_user_as()
        assert data['group'].name == EMPLOYEE

    def test_fake_user_as_with_correct_role(self, ub_with_roles):
        data = ub_with_roles.fake_user_as(role=ENTITY_MANAGER)
        assert data['group'].name == ENTITY_MANAGER

    def test_fake_user_as_with_incorrect_role(self, ub_with_roles):
        with pytest.raises(ObjectDoesNotExist):
            ub_with_roles.fake_user_as(role='unknown role')

    def test_fake_supervisor_default(self, ub_with_roles):
        s = ub_with_roles.fake_supervisor()
        assert s['email'].endswith(EMAIL_SUFFIX)
        assert s['email'].startswith(EMAIL_PREFIX)

    def test_fake_supervisor_with_email(self, ub_with_roles):
        s = ub_with_roles.fake_supervisor(SUPERVISOR_EMAIL)
        assert s['email'] == SUPERVISOR_EMAIL
        assert s['email'].startswith(EMAIL_PREFIX)

    def test_build_user_defaults(self, ub_with_roles):
        u = ub_with_roles.build_user()
        q = User.objects.filter(email=u.email)
        r = User.objects.get(email=u.email)
        assert q.exists()
        assert r.is_employee
        assert r.first_name != ''
        assert email_address_exists(r.email)

    def test_fake_user_with_email_exists(self, ub_with_roles):
        u1 = ub_with_roles.build_user()
        u2 = ub_with_roles.fake_user(email=u1.email)
        assert u1.email != u2['email']

    def test_build_user_with_email(self, ub_with_roles):
        u = ub_with_roles.build_user(email=SUPERVISOR_EMAIL)
        assert User.objects.filter(email=u.email).exists()

    def test_build_user_with_role(self, ub_with_roles):
        u = ub_with_roles.build_user(role=ENTITY_MANAGER)
        assert User.objects.filter(email=u.email).exists()
        r = User.objects.get(email=u.email)
        assert r.is_entity_manager


class TestEmployeeBuilder(BaseTestBuilder):  # tests passed
    @pytest.fixture
    def emb(self, eb):
        return EmployeeBuilder(eb)

    @pytest.fixture
    def emb_with_roles(self, eb_with_roles):
        return EmployeeBuilder(eb_with_roles)

    def test_fake_employee_data_default(self, emb):
        e = emb.fake_employee_data()
        assert e['user'] == ''
        assert e['title'] == '1'
        assert e['phone1'] != ''
        assert e['gender'] == ''


    def test_fake_employee_data_correct_title(self, emb):
        e = emb.fake_employee_data(title='2')
        assert e['user'] == ''
        assert e['title'] == '2'
        assert e['phone1'] != ''
        assert e['gender'] == ''

    def test_fake_employee_data_incorrect_title(self, emb):
        with pytest.raises(ValueError):
            emb.fake_employee_data(title='4')

    def test_fake_employee_as_correct_values(self, emb_with_roles):
        emb_with_roles.entity_builder.build_entity()
        emb_with_roles.entity_builder.build_departments()
        e = emb_with_roles.fake_employee_as(title='1', role_name=EMPLOYEE)

    def test_fake_employee_as_incorrect_role(self, emb_with_roles):
        with pytest.raises(Exception):
            emb_with_roles.fake_employee_as(title='1', role_name='Unknown role')

    def test_create_employee_as_default(self, emb_with_roles):
        emb_with_roles.entity_builder.build_entity()
        emb_with_roles.entity_builder.build_departments()
        e = emb_with_roles.create_employee_as()
        r = Employee.objects.get(pk=e.pk)
        assert r.pk == e.pk
        assert r.user.is_employee

    def test_build(self, emb_with_roles):
        emb_with_roles.entity_builder.build_entity()
        emb_with_roles.entity_builder.build_departments()
        e_list = emb_with_roles.build()
        assert len(e_list) == EMPLOYEE_COUNT


class TestManagerBuilder(BaseTestBuilder):  # tests passed
    @pytest.fixture
    def mb_with_roles(self, eb_with_roles):
        return ManagerBuilder(eb_with_roles)

    def test_build(self, mb_with_roles):
        mb_with_roles.entity_builder.build_entity()
        mb_with_roles.entity_builder.build_departments()
        m_list = mb_with_roles.build()
        assert len(m_list) == MANAGER_COUNT


class TestEntityBuilder(BaseTestBuilder):  # tests passed
    @pytest.fixture
    def test_entity_name(self):
        return 'The Youbee Test Company'

    @pytest.fixture
    def test_supervisor_email(self):
        return 'test.youbee+supervisor@gmail.com'

    def test_init(self, eb):
        assert eb.entity is None
        assert eb.entity_name is not None
        assert eb.entity_supervisor_email is None
        assert eb.d_builder is not None
        assert  type(eb.d_builder).__name__ == 'DepartmentBuilder'
        assert eb.m_builder is not None
        assert type(eb.m_builder).__name__ == 'ManagerBuilder'
        assert eb.e_builder is not None
        assert type(eb.e_builder).__name__ == 'EmployeeBuilder'
        assert eb.department_count == DEPARTMENT_COUNT
        assert eb.manager_count == MANAGER_COUNT
        assert eb.employee_count == EMPLOYEE_COUNT

    def test_set_entity_name_unknown_name(self, eb):
        new_name = 'The Youbee Company'
        assert eb.set_entity_name(new_name) == new_name
        assert eb.entity_name == new_name

    def test_set_entity_supervisor_email_unknown(self, eb):
        new_email = 'test.youbee+supervisor@gmail.com'
        assert eb.set_entity_supervisor_email(new_email) == new_email
        assert eb.entity_supervisor_email == new_email

    def test_set_department_count_correct(self, eb):
        assert eb.set_department_count(5) == 5
        assert eb.department_count == 5

    def test_set_department_count_too_low(self, eb):
        assert eb.set_department_count(1) == DEPARTMENT_COUNT
        assert eb.department_count == DEPARTMENT_COUNT

    def test_set_department_count_too_high(self, eb):
        assert eb.set_department_count(7) == DEPARTMENT_COUNT
        assert eb.department_count == DEPARTMENT_COUNT

    def test_set_employee_count_correct(self, eb):
        assert eb.set_employee_count(30) == 30
        assert eb.employee_count == 30

    def test_set_employee_count_too_low(self, eb):
        assert eb.set_employee_count(0) == EMPLOYEE_COUNT
        assert eb.employee_count == EMPLOYEE_COUNT

    def test_set_manager_count_correct(self, eb):
        assert eb.set_manager_count(2) == 2
        assert eb.manager_count == 2

    def test_set_manager_count_too_low(self, eb):
        assert eb.set_manager_count(0) == MANAGER_COUNT
        assert eb.manager_count == MANAGER_COUNT

    def test_fake_entity_data(self, eb):
        data = eb.fake_entity_data()
        assert data['entity_name'] is not None
        assert data['entity_details'] is not None
        ed = data['entity_details']
        assert ed['entity'] == ''
        assert ed['phone1'] != ''
        assert ed['phone2'] != ''
        assert ed['email1'] != ''
        assert ed['email2'] != ''
        assert ed['address1'] != ''
        assert ed['address2'] != ''
        assert ed['city'] != ''
        assert ed['country'] != ''
        assert ed['zip_code'] != ''

    def test_get_random_department_no_entity(self, eb):
        with pytest.raises(Exception):
            eb.get_random_department()

    def test_get_random_employee_no_entity(self, eb):
        with pytest.raises(Exception):
            eb.get_random_employee()

    def test_set_entity_name_known_name(self):
        pytest.skip('This test needs an entity to be built')

    def test_build_entity(self, eb, test_entity_name):
        eb.set_entity_name(test_entity_name)
        e = eb.build_entity()
        assert e.name == test_entity_name
        assert e.entity_details.phone1 != ''

    def test_build_departments(self, eb, test_entity_name):
        eb.set_entity_name(test_entity_name)
        eb.build_entity()
        d_list = eb.build_departments()
        assert len(d_list) == DEPARTMENT_COUNT + 1
        assert SUPERVISOR_DEPARTMENT in d_list

    def test_build_supervisor(self, eb_with_roles, test_entity_name, test_supervisor_email):
        eb_with_roles.set_entity_name(test_entity_name)
        eb_with_roles.set_entity_supervisor_email(test_supervisor_email)
        eb_with_roles.build_entity()
        eb_with_roles.build_departments()
        s = eb_with_roles.build_supervisor()
        assert s.user.email == test_supervisor_email
        assert s.department.name == SUPERVISOR_DEPARTMENT

    def test_build_managers(self, eb_with_roles, test_entity_name, test_supervisor_email):
        eb_with_roles.set_entity_name(test_entity_name)
        eb_with_roles.set_entity_supervisor_email(test_supervisor_email)
        eb_with_roles.build_entity()
        eb_with_roles.build_departments()
        eb_with_roles.build_supervisor()
        m_list = eb_with_roles.build_managers()
        assert len(m_list) == MANAGER_COUNT

    def test_build_employees(self, eb_with_roles, test_entity_name, test_supervisor_email):
        eb_with_roles.set_entity_name(test_entity_name)
        eb_with_roles.set_entity_supervisor_email(test_supervisor_email)
        eb_with_roles.build_entity()
        eb_with_roles.build_departments()
        eb_with_roles.build_supervisor()
        eb_with_roles.build_managers()
        e_list = eb_with_roles.build_employees()
        assert len(e_list) == EMPLOYEE_COUNT

    def test_build(self, eb_with_roles, test_entity_name, test_supervisor_email):
        eb_with_roles.set_entity_name(test_entity_name)
        eb_with_roles.set_entity_supervisor_email(test_supervisor_email)
        e = eb_with_roles.build()
        assert e is not None
        assert e.name == test_entity_name
        assert e.supervisor.email == test_supervisor_email


class TestDatabaseEngineer:  # tests passed
    @pytest.fixture
    def construct_data(self):
        return {
            'entity_name': None,
            'supervisor_email': None,
            'department_count': None,
            'manager_count': None,
            'employee_count': None,
        }

    # test passed
    def test_construct_entity_defaults(self, init_empty_db):
        deng = DatabaseEngineer()
        e = deng.construct_entity()
        assert e is not None
        assert Entity.objects.count() == 1
        assert e.departments.count() == DEPARTMENT_COUNT + 1
        assert e.employees.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 1

    # test passed
    def test_construct_entity_defaults_data(self, init_empty_db, construct_data):
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert Entity.objects.count() == 1
        assert e.departments.count() == DEPARTMENT_COUNT+1
        assert e.employees.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 1

    # test passed
    def test_construct_entity_with_entity_name(self, init_empty_db, construct_data):
        entity_name = 'The Youbee Test Company'
        construct_data['entity_name'] = entity_name
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert e.name == entity_name
        assert Entity.objects.count() == 1
        assert e.departments.count() == DEPARTMENT_COUNT+1
        assert e.employees.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 1

    # test passed
    def test_construct_entity_with_supervisor_email(self, init_empty_db, construct_data):
        supervisor_email = 'test.youbee+super@gmail.com'
        construct_data['supervisor_email'] = supervisor_email
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert e.supervisor.email == supervisor_email
        assert Entity.objects.count() == 1
        assert User.objects.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 2
        assert e.departments.count() == DEPARTMENT_COUNT+1
        assert e.employees.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 1

    # test passed
    def test_construct_entity_with_department_count(self, init_empty_db, construct_data):
        construct_data['department_count'] = 5
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert Entity.objects.count() == 1
        assert User.objects.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 2
        assert e.departments.count() == 6
        assert e.employees.count() == EMPLOYEE_COUNT + MANAGER_COUNT + 1

    # test passed
    def test_construct_entity_with_employee_count(self, init_empty_db, construct_data):
        construct_data['employee_count'] = 50
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert Entity.objects.count() == 1
        assert User.objects.count() == MANAGER_COUNT + 52
        assert e.departments.count() == DEPARTMENT_COUNT + 1
        assert e.employees.count() == MANAGER_COUNT + 51

    # test passed
    def test_construct_entity_with_manager_count(self, init_empty_db, construct_data):
        construct_data['manager_count'] = 2
        deng = DatabaseEngineer()
        e = deng.construct_entity(**construct_data)
        assert e is not None
        assert Entity.objects.count() == 1
        assert User.objects.count() == EMPLOYEE_COUNT + 4
        assert e.departments.count() == DEPARTMENT_COUNT+1
        assert e.employees.count() == EMPLOYEE_COUNT + 3

    # test passed
    def test_create_test_data(self, init_empty_db, construct_data):
        deng = DatabaseEngineer()
        entity_name = 'The Youbee Test Company'
        supervisor_email = 'test.youbee+super@gmail.com'
        construct_data['entity_name'] = entity_name
        construct_data['supervisor_email'] = supervisor_email
        e1 = deng.construct_entity(**construct_data)
        assert e1 is not None
        assert e1.name == entity_name
        assert e1.supervisor.email == supervisor_email
        assert Entity.objects.count() == 1
        construct_data['entity_name'] = None
        construct_data['supervisor_email'] = None
        e2 = deng.construct_entity(**construct_data)
        assert e2 is not None
        assert e2 is not e1
        assert Entity.objects.count() == 2
        e3 = deng.construct_entity(**construct_data)
        assert e3 is not None
        assert e3 is not e1 and e3 is not e2
        assert Entity.objects.count() == 3
        e4 = deng.construct_entity(department_count=6, manager_count=2, employee_count=50)
        assert e4 is not None
        assert e4 is not e1 and e4 is not e2 and e4 is not e1
        assert Entity.objects.count() == 4
