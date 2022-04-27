# youbee_main/management/commands/create_user_roles.py
# Run command: python manage.py create_user_roles

from django.core.management.base import BaseCommand

from users.roles import create_roles

SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3


class Command(BaseCommand):
    help = ("Create the user roles for the website. ")

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        verbosity = options.get("verbosity", NORMAL)

        if verbosity >= NORMAL:
            self.stdout.write("=== Creating the user roles ===")

        # Do the job
        create_roles()

        if verbosity >= NORMAL:
            self.stdout.write("=== Done ===")
