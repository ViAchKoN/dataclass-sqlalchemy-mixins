# Dataclass Sqlalchemy Mixins
_____
### Package requirements
- `python >= 3.9`
- `pydantic >= 1.9`
- `sqlalchemy >= 1.4.0`
___
### Installation
```bash
# without extras 
pip install dataclass-sqlalchemy-mixins

# with pydantic 
pip install dataclass-sqlalchemy-mixins[pydantic]
```
___
### Description
This package consists of the several important parts: 
1. Helper mixins which directly interacts with SQLAlchemy to apply filters and orderings to a query or get binary/unary SQLAlchemy expressions that can be applied when required
2. Pydantic dataclasses mixins that are used as proxies for helper mixins



___
### Usage
 
It is important to set the `SQLAlchemy` model in the `ConverterConfig` that you are going to query in the dataclass you are creating. 
This package supports sql operations: `eq`, `in`, `not_in`, `gt`, `lt`, `gte`, `lte`, `not`, `is`, `is_not`, `like`, `ilike`, `isnull`. 
To apply a filter to a field, the filter should be formatted like `field_name__{sql_op}`. Filtering though a foreign key supported using `field_name__foreigh_key_field__{sql_op}`.
To perform sorting the value should be passed as `id` to ASC and `-name` to DESC. Inner joins will be applied automatically if using `pydantic` mixins.


**Direct**

It is possible to apply mixins to custom dataclasses by inheriting from either `SqlAlchemyFilterConverterMixin` for filters or `SqlAlchemyOrderConverterMixin` for orderings.

Filter:
```python
import typing

from dataclasses import dataclass, asdict

@dataclass
class CustomDataclass(SqlAlchemyFilterConverterMixin):
    id__gte: int = None
    name__in: typing.List[str] = None
    object__place: int = None 
    
    class ConverterConfig:
        model = SomeModel 
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items() if v is not None}


custom_dataclass = CustomDataclass(
    id__gte=1,
    name__in=['abc', 'def'],
    object__place=1,
)

binary_expression = custom_dataclass.get_binary_expressions(custom_dataclass.dict())

query = query.filter(*binary_expression)
```

Order by:
```python
import typing

from dataclasses import dataclass, asdict

@dataclass
class CustomDataclass(SqlAlchemyOrderConverterMixin):
    order_by: typing.Optional[typing.Optional[str, typing.List[str]]] = None
    
    class ConverterConfig:
        model = SomeModel 
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items() if v is not None}

custom_dataclass = CustomDataclass(
    order_by=['id', '-name']
)

unary_expressions = custom_dataclass.get_unary_expressions(custom_dataclass.order_by)

query = query.order_by(*unary_expressions)
```

**Pydantic**

Filter:
```python
import typing

class CustomBaseModel(SqlAlchemyFilterBaseModel):
    id__gte: int = None
    name__in: typing.List[str] = None
    object__place: int = None 
    
    class ConverterConfig:
        model = SomeModel 
    

custom_dataclass = CustomBaseModel(
    id__gte=1,
    name__in=['abc', 'def'],
    object__place=1,
)

binary_expression = custom_dataclass.to_binary_expressions()

query = query.filter(*binary_expression)

# or

query = query.apply_filters(query=query)
```

Sometimes, it is necessary to manipulate sent data before applying filters. 
For example, a field should not be directly converted to a filter; instead, custom logic should be applied. 
As of version `0.1.3`, the `to_binary_expressions` and `apply_filters` methods accept the `export_params` argument to address this situation. 
Values mentioned in the Pydantic dictionary [export section](https://docs.pydantic.dev/1.10/usage/exporting_models/ ) can be sent as `export_params`.

```python
import typing

class CustomBaseModel(SqlAlchemyFilterBaseModel):
    id__gte: int = None
    name__in: typing.List[str] = None
    filter_to_exclude: typing.Any = None 
    
    class ConverterConfig:
        model = SomeModel 
    

custom_dataclass = CustomBaseModel(
    id__gte=1,
    name__in=['abc', 'def'],
    filter_to_exclude="filter_value",
)

# filter_to_exclude field will be excluded from converting basemodel to sqlalchemy filters

binary_expression = custom_dataclass.to_binary_expressions(
    export_params={'exclude': {'filter_to_exclude'}, }
)

query = query.filter(*binary_expression)

# or

query = query.apply_filters(
    query=query,
    export_params={'exclude': {'filter_to_exclude'}, }
)
```

Order by:
```python
import typing

class CustomBaseModel(SqlAlchemyOrderBaseModel):
    id__gte: int = None
    name__in: typing.List[str] = None
    object__place: int = None 
    
    class ConverterConfig:
        model = SomeModel 
    
custom_dataclass = CustomBaseModel(
    order_by=['id', '-name']
)

unary_expressions = custom_dataclass.get_unary_expressions(custom_dataclass.order_by)

query = query.order_by(*unary_expressions)

# or 

query = query.apply_order_by(query)
```
____
### FastApi support 
Dataclasses inherited from `SqlAlchemyFilterBaseModel` or `SqlAlchemyOrderBaseModel` normally produce the correct documentation. 
However, there is one issue that should be mentioned: 
`FastAPI` has trouble creating documentation when a complex type is set as an annotation for `Query` parameters. 
This includes lists.

The `extra` parameter was introduced to address these situations which can be set in `ConverterConfig`. 
Currently, this parameter only accepts a dictionary with one key: `BaseModelConverterExtraParams.LIST_AS_STRING`. 
This key instructs the converter to treat the passed string as a list in the context of filtering and ordering.

For example, a class defined like this will convert the value passed for `field__in` into a list when applying filters and orderings.
The value passed for `another_field__in` won't be treated a list because the field wasn't included in the `fields` set in `extra`. 

Another parameter can be used is `expected_types`. 
It is used to define which as which type should be elements of the list treated as when a str converted to a list. 
If an expected type is not passed for a field it will be converted to a str.

```python
class SomeSqlAlchemyFilterModel(SqlAlchemyFilterBaseModel):
    field__in: str = Query(None)
    another_field__in: str = Query(None)

    class ConverterConfig:
        model = Item
        extra = {
            BaseModelConverterExtraParams.LIST_AS_STRING: {
                'fields': ['field__in', ],
                'expected_types': {
                    'field__in': int,
                }
            }
        }
```

The same applies to the classes inherited from `SqlAlchemyOrderBaseModel`,
except that since the model accepts only the `order_by` field, it is not necessary to specify specific fields.

```python
class SomeSqlAlchemyOrderModel(SqlAlchemyOrderBaseModel):
    order_by: str = None

    class ConverterConfig:
        model = Item
        extra = {
            BaseModelConverterExtraParams.LIST_AS_STRING: True
        }
```

**Another possible solution**

Also, it is possible not use `ConverterConfig` to correctly display lists in `Query` parameters using `FastApi`

```python
class SomeSqlAlchemyFilterModel(SqlAlchemyFilterBaseModel):
    field__in: str

    def __init__(self, field__in: typing.List[str] = Query(), **kwargs) -> None:
        super().__init__(field__in=field__in, **kwargs)
```

____
### Docker Compose
To run tests on your local machine
```bash
cd tests
docker compose up
```
____
### Links
[Github](https://github.com/ViAchKoN/dataclass-sqlalchemy-mixins)
