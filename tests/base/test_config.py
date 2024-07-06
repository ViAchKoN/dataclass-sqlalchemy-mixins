import pytest

from core.pydantic.sqlalchemy_base_models import SqlAlchemyFiltersBaseModel
from tests.models import Item


def test_filter_model__init__ok():
    class SomeSqlAlchemyFiltersModel(SqlAlchemyFiltersBaseModel):
        class ConverterConfig:
            model = Item

    SomeSqlAlchemyFiltersModel()


def test_filter_model__init__no_filtered_model__error():
    class SomeSqlAlchemyFiltersModel(SqlAlchemyFiltersBaseModel):
        class ConverterConfig:
            model = None

    with pytest.raises(ValueError) as e:
        SomeSqlAlchemyFiltersModel()
    assert str(e.value) == "ConverterConfig param 'model' can't be None"
