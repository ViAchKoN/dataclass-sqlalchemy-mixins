import typing as tp

import pydantic
import pytest

from dataclass_sqlalchemy_mixins.pydantic_mixins.sqlalchemy_base_models import (
    SqlAlchemyFilterBaseModel,
)


pydantic_version = int(pydantic.__version__[0])

if pydantic_version < 2:
    from pydantic.fields import ModelField

    field_class = ModelField
else:
    from pydantic.fields import FieldInfo

    field_class = FieldInfo


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
                new_fields: tp.Dict[str, tp.Union["FieldInfo", "ModelField"]] = {}
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

                    # pydantic_mixins v1
                    if pydantic_version < 2:
                        new_fields[f_name] = field_class.infer(
                            name=f_name,
                            value=f_value,
                            annotation=f_annotation,
                            class_validators=None,
                            config=cls.__config__,
                        )
                    # pydantic_mixins v2
                    else:
                        new_fields[f_name] = field_class(annotation=f_annotation)

                # pydantic_mixins v1
                if pydantic_version < 2:
                    cls.__fields__.update(new_fields)
                    cls.__annotations__ = new_annotations
                # pydantic_mixins v2
                else:
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
