import datetime
import enum
import typing as tp

from pydantic import BaseModel, Extra

from dataclass_sqlalchemy_mixins.base.mixins import (
    SqlAlchemyFilterConverterMixin,
    SqlAlchemyOrderConverterMixin,
)


# We might need to use a custom logic for
# pydantic_mixins models
# for example fastapi not correctly supports
# lists in query params set in base model
# so we can set this fields in extra param in ConverterConfig
class BaseModelConverterExtraParams(str, enum.Enum):
    LIST_AS_STRING = (
        "list_as_string"  # Deal with like a string with delimeter ',' when using dict()
    )


class SqlAlchemyFilterBaseModel(
    BaseModel,
    SqlAlchemyFilterConverterMixin,
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ConverterConfig.model is None:
            raise ValueError("ConverterConfig param 'model' can't be None")

    def _to_dict(self, **kwargs):
        dict_values = self.dict(**kwargs)

        if hasattr(self.ConverterConfig, "extra"):
            for key, value in self.ConverterConfig.extra.items():
                if key == BaseModelConverterExtraParams.LIST_AS_STRING:
                    fields = value.get("fields")
                    expected_types = value.get("expected_types")

                    if fields:
                        for dict_key, dict_value in dict_values.items():
                            if dict_key in fields:
                                expected_type = (
                                    expected_types.get(dict_key)
                                    if expected_types
                                    else str
                                )

                                if expected_type is datetime.datetime:
                                    expected_type = datetime.datetime.fromisoformat

                                value = list(map(str.strip, dict_value.split(",")))

                                dict_values[dict_key] = list(map(expected_type, value))
        return dict_values

    def to_binary_expressions(
        self,
        export_params=None,
    ):
        if export_params is None:
            export_params = dict()

        filters = self._to_dict(exclude_none=True, **export_params)

        return self.get_binary_expressions(
            filters=filters,
        )

    def apply_filters(
        self,
        query,
        export_params=None,
    ):
        if export_params is None:
            export_params = dict()

        filters = self._to_dict(exclude_none=True, **export_params)

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
    order_by: tp.Optional[tp.Union[str, tp.List[str]]] = None

    class Config:
        extra = Extra.forbid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ConverterConfig.model is None:
            raise ValueError("ConverterConfig param 'model' can't be None")

        self._split_list_to_str()

    def _split_list_to_str(self):
        order_by = self.order_by
        if hasattr(self.ConverterConfig, "extra"):
            for key, value in self.ConverterConfig.extra.items():
                if key == BaseModelConverterExtraParams.LIST_AS_STRING:
                    self.order_by = list(map(str.strip, order_by.split(",")))

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
