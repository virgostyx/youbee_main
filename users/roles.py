# youbee_main/users/roles.py

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist

#                0        1        2        3        4
PERMISSIONS = ['view', 'change', 'add', 'delete', 'unlink', ]

VIEW_IDX = 0
CHANGE_IDX = 1
ADD_IDX = 2
DELETE_IDX = 3
UNLINK_IDX = 4

MODELS = ['entitydetail',    # 0
          'department',       # 1
          'employee',         # 2
          'user', ]           # 3

ENTITY_DETAILS_IDX = 0
DEPARTMENT_IDX = 1
EMPLOYEE_IDX = 2
USER_IDX = 3

ROLES = ['Entity Supervisor',  # 0
         'Entity Manager',     # 1
         'Employee',           # 2
         ]

ENTITY_SUPERVISOR = 'Entity Supervisor'
ENTITY_MANAGER = 'Entity Manager'
EMPLOYEE = 'Employee'

ENTITY_SUPERVISOR_ID = '1'
ENTITY_MANAGER_ID = '2'
EMPLOYEE_ID = '3'

ENTITY_SUPERVISOR_IDX = 0
ENTITY_MANAGER_IDX = 1
EMPLOYEE_ROLE_IDX = 2

SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3


def get_group_id(name):
    g = None
    try:
        g = Group.objects.get(name=name)
    except ObjectDoesNotExist:
        print("The group {} does not exist!".format(name))

    return g


def get_permission(perm, model):
    p_name = '{perm}_{model}'.format(perm=perm, model=model)
    p = None
    try:
        p = Permission.objects.get(codename=p_name)
    except ObjectDoesNotExist:
        print("The permission with name={} does not exists".format(p_name))

    return p


def add_permission_to_role(to, perm, model, verbosity=NORMAL):
    if verbosity >= NORMAL:
        print('\tAdd permission ' + perm + ' for model ' + model)

    to.permissions.add(get_permission(perm, model))
    to.save()

    return


def clear_permissions(g, verbosity=NORMAL):
    if verbosity >= NORMAL:
        print('\tClear Permissions')

    g.permissions.clear()

    return


def create_entity_supervisor_role(verbosity=NORMAL):
    # Add entity Supervisor role - this role has absolute control of the entity
    if verbosity >= NORMAL:
        print('Create entity Supervisor Role')

    g, created = Group.objects.get_or_create(name=ROLES[ENTITY_SUPERVISOR_IDX])

    if not created:  # If role exists already, remove all existing permissions
        clear_permissions(g, verbosity)

    # count = 12
    for m in MODELS[DEPARTMENT_IDX:]:  # from department to user
        for p in PERMISSIONS[:UNLINK_IDX]:  # only view, change, add, delete. 
            add_permission_to_role(to=g, perm=p, model=m, verbosity=verbosity)

    # count = 2
    for m in MODELS[DEPARTMENT_IDX:USER_IDX]:  # for department and employee
        add_permission_to_role(to=g, perm=PERMISSIONS[UNLINK_IDX], model=m, verbosity=verbosity)  # only unlink

    # count = 2
    for p in PERMISSIONS[:ADD_IDX]:  # only view, change
        add_permission_to_role(to=g, perm=p, model=MODELS[ENTITY_DETAILS_IDX], verbosity=verbosity)

    # count = 1
    add_permission_to_role(to=g, perm=PERMISSIONS[DELETE_IDX], model='entity', verbosity=verbosity)  # And delete too. No add

    # total count = 17
    return


def create_entity_manager_role(verbosity=NORMAL):
    # Add entity Manager role - this role is the backup of the entity Supervisor
    #  but cannot change the entity details
    if verbosity >= NORMAL:
        print('Create entity Manager Role')

    g, created = Group.objects.get_or_create(name=ROLES[ENTITY_MANAGER_IDX])

    if not created:
        clear_permissions(g)

    #count = 12
    for m in MODELS[DEPARTMENT_IDX:]:  # from department to user
        for p in PERMISSIONS[:UNLINK_IDX]:  # only view, change, add, delete
            add_permission_to_role(to=g, perm=p, model=m, verbosity=verbosity)

    # count = 2
    for m in MODELS[DEPARTMENT_IDX:USER_IDX]:  # for department and employee
        add_permission_to_role(to=g, perm=PERMISSIONS[UNLINK_IDX], model=m, verbosity=verbosity)  # only unlink

    # count = 1
    add_permission_to_role(to=g, perm=PERMISSIONS[VIEW_IDX], model=MODELS[ENTITY_DETAILS_IDX], verbosity=verbosity)  # only view

    # total count = 15 -> 32
    return


def create_employee_role(verbosity=NORMAL):
    # Add employee role - this role has a view only role
    #  but cannot change the entity details
    if verbosity == NORMAL:
        print('Create employee Role')

    g, created = Group.objects.get_or_create(name=ROLES[EMPLOYEE_ROLE_IDX])

    if not created:
        clear_permissions(g)

    # count = 3
    for m in MODELS[DEPARTMENT_IDX:]:  # from department to user
        add_permission_to_role(to=g, perm=PERMISSIONS[VIEW_IDX], model=m, verbosity=verbosity)  # only view

    # count = 1
    add_permission_to_role(to=g, perm=PERMISSIONS[VIEW_IDX], model=MODELS[ENTITY_DETAILS_IDX], verbosity=verbosity)  # only view

    # total count = 4 -> 36
    return


def create_roles(verbosity=NORMAL):
    create_entity_supervisor_role(verbosity)
    create_entity_manager_role(verbosity)
    create_employee_role(verbosity)
