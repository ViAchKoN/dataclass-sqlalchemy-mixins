import typing as tp

from pydantic import BaseModel
from sqlalchemy import BinaryExpression, Select
from sqlalchemy.orm import DeclarativeMeta, Query

from core.base import SqlAlchemyFilterConverter


class SqlAlchemyFiltersModel(BaseModel, SqlAlchemyFilterConverter):
    class ConverterConfig:
        model: tp.Type[DeclarativeMeta] = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if self.ConverterConfig.model is None:
            raise ValueError("Config param 'model' can't be None")

    def to_sql(self) -> tp.List[BinaryExpression]:
        filters = self.dict(exclude_none=True)

        return self.get_filters_binary_expressions(
            model=self.ConverterConfig.model,
            filters=filters,
        )

    def apply_filters(
        self,
        query: tp.Union[Select, Query],
    ) -> tp.Union[Select, Query]:
        filters = self.dict(exclude_none=True)

        filters_binary_expressions = self.get_filters_binary_expressions(
            model=self.ConverterConfig.model,
            filters=filters,
        )
        query = query.filter(*filters_binary_expressions)
        return query


class SqlAlchemyOrderingsMixin:
    def to_sql(self):
        pass
