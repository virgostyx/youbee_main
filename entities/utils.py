# youbee_main/entities/utils.py

# System libraries

# Third-party libraries

# Django modules

# Django apps

#  Current app modules


def get_entity_from_user(user):
    return user.entity if user.is_entity_supervisor else user.employee.entity