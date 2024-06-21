import pytest

from core.sqlalchemy_base_models import SqlAlchemyFiltersModel
from tests.models import Item


def test_filter_model__init__ok():

    class SomeSqlAlchemyFiltersModel(SqlAlchemyFiltersModel):
        class Config:
            filtered_model = Item

    SomeSqlAlchemyFiltersModel()


def test_filter_model__init__no_filtered_model__error():

    class SomeSqlAlchemyFiltersModel(SqlAlchemyFiltersModel):
        class Config:
            filtered_model = None

    with pytest.raises(ValueError) as e:
        SomeSqlAlchemyFiltersModel()
        assert str(e.value) == "Config param 'filtered_model' can't be None"
