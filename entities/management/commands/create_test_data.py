# entities/management/commands/create_test_data.py

# System libraries
import time

# Third-party libraries

# Django modules
from django.core.management.base import BaseCommand

# Django apps


# Current app modules
from .constants import SUPERVISOR_EMAIL
from .builders import DatabaseEngineer


SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3


class Command(BaseCommand):
    help = "Create test data "

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        verbosity = options.get("verbosity", NORMAL)

        if verbosity >= NORMAL:
            self.stdout.write("=== Creating 4 fake entities ===")

        command_start_time = time.time()

        # Do the job
        deng = DatabaseEngineer()

        if verbosity >= NORMAL:
            self.stdout.write("=== Creating The Youbee Test Company ===")

        entity_start_time = time.time()
        deng.construct_entity(entity_name='The Youbee Test Company', supervisor_email=SUPERVISOR_EMAIL)

        if verbosity >= NORMAL:
            self.stdout.write("=== Created in %.2f seconds ===" % (time.time() - entity_start_time))
            entity_start_time = time.time()
            self.stdout.write("=== Creating a second fake entity ===")

        deng.construct_entity()

        if verbosity >= NORMAL:
            self.stdout.write("=== Created in %.2f seconds ===" % (time.time() - entity_start_time))
            entity_start_time = time.time()
            self.stdout.write("=== Creating a big entity ===")

        deng.construct_entity(department_count=6, manager_count=2, employee_count=50)

        if verbosity >= NORMAL:
            self.stdout.write("=== Created in %.2f seconds ===" % (time.time() - entity_start_time))
            entity_start_time = time.time()
            self.stdout.write("=== Creating a last fake entity ===")

        deng.construct_entity()

        if verbosity >= NORMAL:
            self.stdout.write("=== Created in %.2f seconds ===" % (time.time() - entity_start_time))
            self.stdout.write("=== Done in %.2f seconds ===" % (time.time() - command_start_time))
