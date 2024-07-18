import typing as tp

import pytest

from core.pydantic.sqlalchemy_base_models import SqlAlchemyOrderBaseModel


@pytest.fixture
def get_sqlalchemy_order_base_model():
    def sqlalchemy_order_base_model(
        base_model,
        model_kwargs: tp.Dict[str, tp.Any],
    ):
        class CustomSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
            class ConverterConfig:
                model = base_model

        custom_sqlalchemy_filters_model = CustomSqlAlchemyOrderModel(**model_kwargs)
        return custom_sqlalchemy_filters_model

    return sqlalchemy_order_base_model
