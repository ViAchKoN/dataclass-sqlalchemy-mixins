import pytest
from pydantic import ValidationError

from core.pydantic.sqlalchemy_base_models import (
    SqlAlchemyFilterBaseModel,
    SqlAlchemyOrderBaseModel,
)
from tests.models import Item


def test_filter_model__init__ok():
    class SomeSqlAlchemyFiltersModel(SqlAlchemyFilterBaseModel):
        class ConverterConfig:
            model = Item

    SomeSqlAlchemyFiltersModel()


def test_filter_model__init__no_filtered_model__error():
    class SomeSqlAlchemyFiltersModel(SqlAlchemyFilterBaseModel):
        class ConverterConfig:
            model = None

    with pytest.raises(ValueError) as e:
        SomeSqlAlchemyFiltersModel()
    assert str(e.value) == "ConverterConfig param 'model' can't be None"


def test_order_model__init__ok():
    class SomeSqlAlchemySortModel(SqlAlchemyOrderBaseModel):
        class ConverterConfig:
            model = Item

    SomeSqlAlchemySortModel()


def test_order_model__init__no_filtered_model__error():
    class SomeSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
        class ConverterConfig:
            model = None

    with pytest.raises(ValueError) as e:
        SomeSqlAlchemyOrderModel()
    assert str(e.value) == "ConverterConfig param 'model' can't be None"


def test_order_model__extra_fields():
    class SomeSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
        class ConverterConfig:
            model = None

    field_kwargs = {"order_by": 123, "extra_field": 123}

    with pytest.raises(ValidationError):
        SomeSqlAlchemyOrderModel(**field_kwargs)
