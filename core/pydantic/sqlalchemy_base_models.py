import typing as tp

from pydantic import BaseModel, Extra, Field

from core.base.mixins import (
    SqlAlchemyFilterConverterMixin,
    SqlAlchemyOrderConverterMixin,
)


class SqlAlchemyFilterBaseModel(BaseModel, SqlAlchemyFilterConverterMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ConverterConfig.model is None:
            raise ValueError("ConverterConfig param 'model' can't be None")

    def to_binary_expressions(self):
        filters = self.dict(exclude_none=True)

        return self.get_binary_expressions(
            filters=filters,
        )

    def apply_filters(
        self,
        query,
    ):
        filters = self.dict(exclude_none=True)

        filters_binary_expressions = self.get_models_binary_expressions(
            filters=filters,
        )

        models_to_join = []
        binary_expressions = []

        for binary_expression in filters_binary_expressions:
            models_to_join += binary_expression["models"]
            binary_expressions.append(binary_expression["binary_expression"])

        # Checking if there are other models required to be joined
        if models_to_join != [
            self.ConverterConfig.model,
        ]:
            query = self.join_models(query=query, models=models_to_join)

        query = query.filter(*binary_expressions)
        return query


class SqlAlchemyOrderBaseModel(BaseModel, SqlAlchemyOrderConverterMixin):
    order_by: tp.Union[str, tp.List[str]] = Field(
        None, description="A list of fields or a field on which to order a query"
    )

    class Config:
        extra = Extra.forbid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ConverterConfig.model is None:
            raise ValueError("ConverterConfig param 'model' can't be None")

    def to_unary_expressions(self):
        order_by = self.order_by

        return self.get_unary_expressions(
            order_by=order_by,
        )

    def apply_order_by(
        self,
        query,
    ):
        order_by = self.order_by

        order_by_unary_expressions = self.get_models_unary_expressions(
            order_by=order_by,
        )

        models_to_join = []
        unary_expressions = []

        for binary_expression in order_by_unary_expressions:
            models_to_join += binary_expression["models"]
            unary_expressions.append(binary_expression["unary_expression"])

        # Checking if there are other models required to be joined
        if models_to_join != [
            self.ConverterConfig.model,
        ]:
            query = self.join_models(query=query, models=models_to_join)

        query = query.order_by(*unary_expressions)
        return query
