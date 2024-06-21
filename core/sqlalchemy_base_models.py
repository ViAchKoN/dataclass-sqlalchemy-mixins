import typing as tp

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


SQLALCHEMY_OP_MATCHER = {
    "eq": "__eq__",
    "in": "in_",
    "not_in": "not_in",
    "gt": "__gt__",
    "lt": "__lt__",
    "gte": "__ge__",
    "lte": "__le__",
    "not": "__ne__",
    "is": "is_",
    "is_not": "is_not",
    "like": "like",
    "ilike": "ilike",
}


class SqlAlchemyFiltersModel(BaseModel):
    class Config:
        filtered_model: tp.Type[DeclarativeBase] = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if self.Config.filtered_model is None:
            raise ValueError("Config param 'filtered_model' can't be None")

    def to_sql(self):
        query_filters = []

        filters = self.dict(exclude_none=True)  # type: ignore
        for field, value in filters.items():
            sql_op = SQLALCHEMY_OP_MATCHER.get("eq")

            if "__" in field:
                field, op = field.split("__")
                sql_op = SQLALCHEMY_OP_MATCHER.get(op)

                if sql_op is None:
                    raise KeyError(
                        f"Unsupported sql operation provided. Supported {', '.join(list(SQLALCHEMY_OP_MATCHER.keys()))}"
                    )
                if op in ["like", "ilike"]:
                    value = "%" + value + "%"

            db_field = getattr(self.Config.filtered_model, field)

            query_filters.append(getattr(db_field, sql_op)(value))
        return query_filters


class SqlAlchemyOrderingsMixin:
    def to_sql(self):
        pass
