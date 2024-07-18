import typing as tp

import pytest
from pydantic.fields import FieldInfo

from core.pydantic.sqlalchemy_base_models import SqlAlchemyFilterBaseModel


@pytest.fixture
def get_sqlalchemy_filter_base_model():
    def sqlalchemy_filter_base_model(
        base_model,
        field_kwargs: tp.Dict[type, tp.Any],
        model_kwargs: tp.Dict[str, tp.Any],
    ):
        class CustomSqlAlchemyFilterModel(SqlAlchemyFilterBaseModel):
            class ConverterConfig:
                model = base_model

            @classmethod
            def add_fields(cls, **field_definitions: tp.Any):
                new_fields: tp.Dict[str, FieldInfo] = {}
                new_annotations: tp.Dict[str, tp.Optional[type]] = {}

                for f_name, f_def in field_definitions.items():
                    if isinstance(f_def, tuple):
                        try:
                            f_annotation, f_value = f_def
                        except ValueError as e:
                            raise Exception(
                                "field definitions should either be a tuple of (<type>, <default>) or just a "
                                "default value, unfortunately this means tuples as "
                                "default values are not allowed"
                            ) from e
                    else:
                        f_annotation, f_value = None, f_def  # noqa:F841

                    if f_annotation:
                        new_annotations[f_name] = f_annotation

                    new_fields[f_name] = FieldInfo(annotation=f_annotation)

                cls.model_fields.update(new_fields)
                cls.model_rebuild(force=True)

        custom_sqlalchemy_filters_model = CustomSqlAlchemyFilterModel()

        custom_sqlalchemy_filters_model.add_fields(
            **field_kwargs,
        )

        for key, value in model_kwargs.items():
            setattr(custom_sqlalchemy_filters_model, key, value)
        return custom_sqlalchemy_filters_model

    return sqlalchemy_filter_base_model
