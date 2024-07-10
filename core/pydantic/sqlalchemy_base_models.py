from pydantic import BaseModel

from core.base.mixins import SqlAlchemyFilterConverterMixin


class SqlAlchemyFiltersBaseModel(BaseModel, SqlAlchemyFilterConverterMixin):
    def __init__(self, *args, **kwargs):
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
