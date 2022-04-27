# youbee_main/entities/fixtures.py

# System libraries


# Third-party libraries
from allauth.account.models import EmailAddress

# Django modules


# Django apps


# Current app modules
from .models import User


class UserFixtures:

    def get_username(self, first_name, last_name):
        return last_name[:5].lower() + first_name[:2].lower()

    def create_user(self, data, group=None):
        user = User.objects.create_user(**data)
        user.username = self.get_username(user.first_name, user.last_name)

        if group:
            user.groups.add(group)

        user.save()

        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        return user

    def create_superuser(self):
        superuser = {
            'email': 'virgostyx@gmail.com',
            'first_name': 'Virgo',
            'last_name': 'STYX',
            'password': 'N0ur1a1505',
        }

        user = User.objects.create_superuser(superuser['email'], superuser['password'])
        user.first_name = superuser['first_name']
        user.last_name = superuser['last_name']
        user.username = 'virgostyx'
        user.save()

        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        return user


user_fixtures = UserFixtures()
