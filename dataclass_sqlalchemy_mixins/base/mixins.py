import typing as tp

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeMeta, InstrumentedAttribute


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
    "isnull": "isnull",
}


class SqlAlchemyBaseConverterMixin:
    class ConverterConfig:
        model: tp.Type[DeclarativeMeta] = None
        extra: tp.Dict[tp.Any, tp.Dict] = None

    def get_foreign_key_filtered_column(
        self,
        models_path_to_look: tp.List[str],
    ) -> tp.Tuple[tp.List[DeclarativeMeta], tp.Union[None, InstrumentedAttribute]]:
        model = self.ConverterConfig.model

        # There might more than one relationship
        # so we need to save a path to the target model
        models = []

        for path in models_path_to_look:

            model_attrs = inspect(model)

            model_relationships = getattr(model_attrs, "relationships", None)

            if model_relationships:
                related_model = getattr(inspect(model).relationships, path, None)

                if related_model:
                    # Updating original model to continue search
                    model = related_model.argument
                    models.append(model)
                    continue

            # If related model is None
            # we might come to field required filtering
            foreign_key_db_column = getattr(model, path, None)
            return models, foreign_key_db_column

        return models, None

    def join_models(self, query, models: tp.List[DeclarativeMeta]):
        query = query

        joined_models = []
        join_methods = [
            "_join_entities",  # sqlalchemy <= 1.3
            "_legacy_setup_joins",  # sqlalchemy == 1.4
            "_setup_joins",  # sqlalchemy == 2.0
        ]
        for join_method in join_methods:
            if hasattr(query, join_method):
                joined_models = [
                    join[0].entity_namespace for join in getattr(query, join_method)
                ]
                # Different sqlalchemy versions might have several join methods
                # but only one of them will return correct joined models list
                if joined_models:
                    break

        for model in models:
            if model != self.ConverterConfig.model and model not in joined_models:
                query = query.join(model)

        return query


class SqlAlchemyFilterConverterMixin(SqlAlchemyBaseConverterMixin):
    DEFAULT_SQLALCHEMY_SQL_OP = SQLALCHEMY_OP_MATCHER.get("eq")

    def _get_filter_binary_expression(
        self,
        field: str,
        value: tp.Any,
    ):
        db_field = None
        sql_op = None
        models = []

        if "__" in field:
            # There might be several relationship
            # that is why string might look like
            # related_model1__related_model2__related_model2_field(?__op)
            filter_params = field.split("__")

            # Op should be always the last one
            last_param = filter_params[-1]

            sql_op = SQLALCHEMY_OP_MATCHER.get(last_param)

            if sql_op == "isnull":
                sql_op = (
                    SQLALCHEMY_OP_MATCHER.get("is")
                    if value
                    else SQLALCHEMY_OP_MATCHER.get("is_not")
                )
                value = None

            if sql_op:
                filter_params = filter_params[:-1]

            if len(filter_params) > 1:
                models, db_field = self.get_foreign_key_filtered_column(
                    models_path_to_look=filter_params,
                )
                if db_field is None:
                    raise ValueError
            else:
                field = filter_params[0]

        if db_field is None:
            db_field = getattr(self.ConverterConfig.model, field)

        if sql_op is None:
            sql_op = self.DEFAULT_SQLALCHEMY_SQL_OP

        models = models or [
            self.ConverterConfig.model,
        ]

        return models, getattr(db_field, sql_op)(value)

    def get_models_binary_expressions(
        self, filters: tp.Dict[str, tp.Any], model: DeclarativeMeta = None
    ):
        if model:
            self.ConverterConfig.model = model

        if self.ConverterConfig.model is None:
            raise ValueError(
                "ConverterConfig.model value can't be None. "
                "Either pass the model parameter or set the ConverterConfig.model."
            )

        model_filters = []

        for field, value in filters.items():
            models, filter_binary_expression = self._get_filter_binary_expression(
                field=field,
                value=value,
            )
            model_filters.append(
                {
                    "models": models,
                    "binary_expression": filter_binary_expression,
                }
            )
        return model_filters

    def get_binary_expressions(
        self,
        filters: tp.Dict[str, tp.Any],
        model: DeclarativeMeta = None,
    ):
        return [
            binary_expression["binary_expression"]
            for binary_expression in self.get_models_binary_expressions(
                filters=filters,
                model=model,
            )
        ]


class SqlAlchemyOrderConverterMixin(SqlAlchemyBaseConverterMixin):
    def _get_order_unary_expression(
        self,
        field,
    ):
        db_field = None

        sql_order_by_direction = "asc"

        if field.startswith("-"):
            sql_order_by_direction = "desc"
            field = field[1:]

        models = []

        if "__" in field:
            # There might be several relationship
            # that is why string might look like
            # related_model1__related_model2__related_model2_field
            order_params = field.split("__")

            if len(order_params) > 1:
                models, db_field = self.get_foreign_key_filtered_column(
                    models_path_to_look=order_params,
                )
                if db_field is None:
                    raise ValueError
            else:
                field = order_params[0]

        if db_field is None:
            db_field = getattr(self.ConverterConfig.model, field)

        models = models or [
            self.ConverterConfig.model,
        ]

        return models, getattr(db_field, sql_order_by_direction)()

    def get_models_unary_expressions(
        self,
        order_by: tp.Union[tp.Any, tp.List],
        model: DeclarativeMeta = None,
    ):
        if model:
            self.ConverterConfig.model = model

        if self.ConverterConfig.model is None:
            raise ValueError(
                "ConverterConfig.model value can't be None. "
                "Either pass the model parameter or set the ConverterConfig.model."
            )

        model_order_by = []

        if isinstance(order_by, str):
            order_by = [
                order_by,
            ]

        for field in order_by:
            field = str(field)

            models, filter_binary_expression = self._get_order_unary_expression(
                field=field,
            )
            model_order_by.append(
                {
                    "models": models,
                    "unary_expression": filter_binary_expression,
                }
            )
        return model_order_by

    def get_unary_expressions(
        self, order_by: tp.Union[str, tp.List[str]], model: DeclarativeMeta = None
    ):
        return [
            binary_expression["unary_expression"]
            for binary_expression in self.get_models_unary_expressions(
                order_by=order_by,
                model=model,
            )
        ]
