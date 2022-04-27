# youbee_main/fixtures/builders/base_builder.py

# System libraries
import abc

# Third-party libraries
from faker import Faker

# Django modules

# Django apps

#  Current app modules


class BaseFakeDataBuilder(metaclass=abc.ABCMeta):
    def __init__(self):
        self.faker = Faker()
        Faker.seed(0)

    @abc.abstractmethod
    def build(self):
        pass


class BaseEntityBuilder(BaseFakeDataBuilder):
    def __init__(self, e_builder=None):
        super().__init__()
        self.entity_builder = e_builder

    def set_entity_builder(self, entity_builder=None):
        if entity_builder is not None:
            self.entity_builder = entity_builder

            return self.entity_builder

    def build(self):
        pass