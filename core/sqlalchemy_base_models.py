import typing as tp

from pydantic import BaseModel
from sqlalchemy import BinaryExpression

from core.base import SqlAlchemyFilterConverter


class SqlAlchemyFiltersModel(BaseModel, SqlAlchemyFilterConverter):
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


class SqlAlchemyOrderingsMixin:
    def to_sql(self):
        pass
