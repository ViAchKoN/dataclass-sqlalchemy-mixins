import pytest
from pydantic import ValidationError

from dataclass_sqlalchemy_mixins.pydantic_mixins.sqlalchemy_base_models import (
    BaseModelConverterExtraParams,
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


def test_filter_model__with_extra_config_params():
    class SomeSqlAlchemyFilterModel(SqlAlchemyFilterBaseModel):
        field__in: str = None

        class ConverterConfig:
            model = Item
            extra = {
                BaseModelConverterExtraParams.LIST_AS_STRING: {"fields": "field__in"}
            }

    field_kwargs = {"field__in": "value_1, value_2, value_3"}
    dict_values = SomeSqlAlchemyFilterModel(**field_kwargs)._to_dict()

    assert dict_values == {"field__in": ["value_1", "value_2", "value_3"]}


def test_filter_model__without_extra_config_params():
    class SomeSqlAlchemyFilterModel(SqlAlchemyFilterBaseModel):
        field__in: str = None

        class ConverterConfig:
            model = Item

    field_kwargs = {"field__in": "value_1, value_2, value_3"}
    dict_values = SomeSqlAlchemyFilterModel(**field_kwargs)._to_dict()

    assert dict_values == {"field__in": "value_1, value_2, value_3"}


def test_order_model__init__ok():
    class SomeSqlAlchemySortModel(SqlAlchemyOrderBaseModel):
        class ConverterConfig:
            model = Item

    SomeSqlAlchemySortModel()


def test_order_model__init__no_order_model__error():
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


def test_order_model__with_extra_config_params():
    class SomeSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
        order_by: str = None

        class ConverterConfig:
            model = Item
            extra = {BaseModelConverterExtraParams.LIST_AS_STRING: None}

    field_kwargs = {"order_by": "value_1, value_2, value_3"}

    order_model = SomeSqlAlchemyOrderModel(**field_kwargs)
    assert order_model.order_by == ["value_1", "value_2", "value_3"]


def test_order_model__without_extra_config_params():
    class SomeSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
        order_by: str = None

        class ConverterConfig:
            model = Item

    field_kwargs = {"order_by": "value_1, value_2, value_3"}

    order_model = SomeSqlAlchemyOrderModel(**field_kwargs)
    assert order_model.order_by == "value_1, value_2, value_3"
