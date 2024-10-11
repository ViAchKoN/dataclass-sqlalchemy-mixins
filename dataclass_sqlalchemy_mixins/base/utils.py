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


def apply_filters(
    query,
    filters: tp.Dict[str, tp.Any],
    model: tp.Type[DeclarativeMeta] = None,
):
    converter = SqlAlchemyFilterConverterMixin()

    filters_binary_expressions = converter.get_models_binary_expressions(
        model=model,
        filters=filters,
    )

    models_to_join = []
    binary_expressions = []

    for binary_expression in filters_binary_expressions:
        models_to_join += binary_expression["models"]
        binary_expressions.append(binary_expression["binary_expression"])

    # Checking if there are other models required to be joined
    if models_to_join != [
        model,
    ]:
        query = converter.join_models(query=query, models=models_to_join)

    query = query.filter(*binary_expressions)
    return query


def apply_order_by(
    query,
    order_by: tp.Union[str, tp.List[str]],
    model: tp.Type[DeclarativeMeta] = None,
):
    converter = SqlAlchemyOrderConverterMixin()

    order_by_unary_expressions = converter.get_models_unary_expressions(
        model=model,
        order_by=order_by,
    )

    models_to_join = []
    unary_expressions = []

    for binary_expression in order_by_unary_expressions:
        models_to_join += binary_expression["models"]
        unary_expressions.append(binary_expression["unary_expression"])

    # Checking if there are other models required to be joined
    if models_to_join != [
        model,
    ]:
        query = converter.join_models(query=query, models=models_to_join)

    query = query.order_by(*unary_expressions)
    return query
