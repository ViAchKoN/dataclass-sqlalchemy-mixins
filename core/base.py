import typing as tp

from sqlalchemy import BinaryExpression, inspect
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


class SqlAlchemyFilterConverter:
    class ConverterConfig:
        model: tp.Type[DeclarativeMeta] = None

    DEFAULT_SQLALCHEMY_SQL_OP = SQLALCHEMY_OP_MATCHER.get("eq")

    @staticmethod
    def get_foreign_key_filtered_column(
        model: tp.Type[DeclarativeMeta],
        models_path_to_look: tp.List[str],
    ) -> tp.Union[None, InstrumentedAttribute]:
        for path in models_path_to_look:
            model_attrs = inspect(model)

            model_relationships = getattr(model_attrs, "relationships", None)

            if model_relationships:
                related_model = getattr(inspect(model).relationships, path, None)

                if related_model:
                    # Updating original model to continue search
                    model = related_model.argument
                    continue

            # If related model is None
            # we might come to field required filtering
            foreign_key_db_column = getattr(model, path, None)
            return foreign_key_db_column

        return related_model

    @classmethod
    def get_filters_binary_expressions(
        cls,
        model: tp.Type[DeclarativeMeta],
        filters: tp.Dict[str, tp.Any],
    ) -> tp.List[BinaryExpression]:
        db_field = None
        sql_op = None
        query_filters = []

        for field, value in filters.items():
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
                    db_field = cls.get_foreign_key_filtered_column(
                        model=model,
                        models_path_to_look=filter_params,
                    )
                    if db_field is None:
                        raise ValueError
                else:
                    field = filter_params[0]

                # It could be related model field in the end,
                # that is why we need to check that
                # if sql_op is None:

                # raise KeyError(
                #     f"Unsupported sql operation provided. Supported {', '.join(list(SQLALCHEMY_OP_MATCHER.keys()))}"
                # )
            if db_field is None:
                db_field = getattr(model, field)

            if sql_op is None:
                sql_op = cls.DEFAULT_SQLALCHEMY_SQL_OP
            query_filters.append(getattr(db_field, sql_op)(value))
        return query_filters
