# youbee_main/fixtures/builders/tests/test_base_builder.py

# System libraries

# Third-party libraries

# Django modules

# Django apps

#  Current app modules
import pytest

from ..base_builder import BaseEntityBuilder


class TestBaseEntityBuilder:  # tests passed
    @pytest.fixture
    def beb(self):
        beb = BaseEntityBuilder()
        return beb

    def test_init(self, beb):
        assert beb.entity_builder is None

    def test_init_with_parameter(self):
        param = BaseEntityBuilder()
        beb = BaseEntityBuilder(param)
        assert beb.entity_builder == param

    def test_set_entity_builder(self, beb):
        param = BaseEntityBuilder()
        beb.set_entity_builder(param)
        assert beb.entity_builder == param

    def test_init_faker(self, beb):
        assert beb.faker is not None
        assert type(beb.faker) is not 'faker.proxy.Faker'
