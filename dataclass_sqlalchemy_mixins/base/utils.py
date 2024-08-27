import typing as tp

from sqlalchemy.orm import DeclarativeMeta

from dataclass_sqlalchemy_mixins.base.mixins import (
    SqlAlchemyFilterConverterMixin,
    SqlAlchemyOrderConverterMixin,
)


def get_binary_expressions(
    filters: tp.Dict[str, tp.Any],
    model: tp.Type[DeclarativeMeta] = None,
):
    return SqlAlchemyFilterConverterMixin().get_binary_expressions(
        filters=filters, model=model
    )


def get_unary_expressions(
    order_by: tp.Union[str, tp.List[str]],
    model: tp.Type[DeclarativeMeta] = None,
):
    return SqlAlchemyOrderConverterMixin().get_unary_expressions(
        order_by=order_by, model=model
    )
