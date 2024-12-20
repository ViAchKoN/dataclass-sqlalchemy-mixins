import datetime
import datetime as dt
import typing as tp
from dataclasses import asdict, dataclass

import pytest
from sqlalchemy import select

from dataclass_sqlalchemy_mixins.base import utils
from dataclass_sqlalchemy_mixins.base.mixins import SqlAlchemyFilterConverterMixin
from dataclass_sqlalchemy_mixins.pydantic_mixins.sqlalchemy_base_models import (
    BaseModelConverterExtraParams,
)
from tests import models, models_factory


def test_filter__dataclass__eq__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
):
    expected_item_name = "expected_item_name"

    # Create expected item
    expected_item = models_factory.ItemFactory.create(name=expected_item_name)

    # Create unexpected items
    models_factory.ItemFactory.create_batch(size=4)

    @dataclass
    class CustomDataclass(SqlAlchemyFilterConverterMixin):
        name: str = None

        class ConverterConfig:
            model = models.Item

        def dict(self):
            return {k: str(v) for k, v in asdict(self).items() if v is not None}

    custom_dataclass = CustomDataclass(name=expected_item_name)

    assert db_session.query(models.Item).count() == 5

    results = (
        db_session.query(models.Item)
        .filter(*custom_dataclass.get_binary_expressions(custom_dataclass.dict()))
        .all()
    )

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()


def test_filter__utils__eq__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
):
    expected_item_name = "expected_item_name"

    # Create expected item
    expected_item = models_factory.ItemFactory.create(name=expected_item_name)

    # Create unexpected items
    models_factory.ItemFactory.create_batch(size=4)

    assert db_session.query(models.Item).count() == 5

    results = (
        db_session.query(models.Item)
        .filter(
            *utils.get_binary_expressions(
                filters={
                    "name": expected_item_name,
                },
                model=models.Item,
            )
        )
        .all()
    )

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()


def test_filter__utils__apply__eq__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
):
    expected_item_name = "expected_item_name"

    # Create expected item
    expected_item = models_factory.ItemFactory.create(name=expected_item_name)

    # Create unexpected items
    models_factory.ItemFactory.create_batch(size=4)

    assert db_session.query(models.Item).count() == 5

    query = db_session.query(models.Item)

    query = utils.apply_filters(
        query=query,
        filters={
            "name": expected_item_name,
        },
        model=models.Item,
    )

    results = query.all()

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__eq__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    expected_item_name = "expected_item_name"

    # Create expected item
    expected_item = models_factory.ItemFactory.create(name=expected_item_name)

    # Create unexpected items
    models_factory.ItemFactory.create_batch(size=4)

    filters_model = get_sqlalchemy_filter_base_model(
        base_model=models.Item,
        field_kwargs={
            "name": (str, ...),
        },
        model_kwargs={
            "name": expected_item_name,
        },
    )

    assert db_session.query(models.Item).count() == 5

    if apply_filters:
        query = select(models.Item)
        query = filters_model.apply_filters(query=query)
        results = db_session.execute(query).scalars().all()
    else:
        results = (
            db_session.query(models.Item)
            .filter(*filters_model.to_binary_expressions())
            .all()
        )

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__in_not_in__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    first_number = 1
    first_item = models_factory.ItemFactory.create(
        number=first_number,
    )

    second_number = 2
    second_item = models_factory.ItemFactory.create(
        number=second_number,
    )

    third_number = 3
    third_item = models_factory.ItemFactory.create(
        number=third_number,
    )

    fourth_number = 4
    fourth_item = models_factory.ItemFactory.create(
        number=4,
    )

    fifth_number = 5
    fifth_item = models_factory.ItemFactory.create(
        number=5,
    )

    assert db_session.query(models.Item).count() == 5

    for field, expected_items in (
        ("number__in", [fourth_item, fifth_item]),
        ("number__not_in", [first_item, second_item, third_item]),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (tp.List[int], ...),
            },
            model_kwargs={
                field: [fourth_number, fifth_number],
            },
        )

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__in_not_in__list_as_string__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    first_number = 1
    first_item = models_factory.ItemFactory.create(
        number=first_number,
    )

    second_number = 2
    second_item = models_factory.ItemFactory.create(
        number=second_number,
    )

    third_number = 3
    third_item = models_factory.ItemFactory.create(
        number=third_number,
    )

    fourth_number = 4
    fourth_item = models_factory.ItemFactory.create(
        number=4,
    )

    fifth_number = 5
    fifth_item = models_factory.ItemFactory.create(
        number=5,
    )

    assert db_session.query(models.Item).count() == 5

    for field, expected_items in (
        ("number__in", [fourth_item, fifth_item]),
        ("number__not_in", [first_item, second_item, third_item]),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (str, ...),
            },
            model_kwargs={
                field: f"{fourth_number}, {fifth_number}",
            },
        )

        filters_model.ConverterConfig.extra = {
            BaseModelConverterExtraParams.LIST_AS_STRING: {
                "fields": [
                    field,
                ],
                "expected_types": {
                    field: int,
                },
            }
        }

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__in_not_in__dates__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    now = dt.datetime.now()

    first_date = now + dt.timedelta(days=1)
    first_item = models_factory.ItemFactory.create(
        created_at=first_date,
    )

    second_date = now + dt.timedelta(days=2)
    second_item = models_factory.ItemFactory.create(
        created_at=second_date,
    )

    third_date = now + dt.timedelta(days=3)
    third_item = models_factory.ItemFactory.create(
        created_at=third_date,
    )

    fourth_date = now + dt.timedelta(days=4)
    fourth_item = models_factory.ItemFactory.create(
        created_at=fourth_date,
    )

    fifth_date = now + dt.timedelta(days=5)
    fifth_item = models_factory.ItemFactory.create(
        created_at=fifth_date,
    )

    assert db_session.query(models.Item).count() == 5

    for field, expected_items in (
        ("created_at__in", [fourth_item, fifth_item]),
        ("created_at__not_in", [first_item, second_item, third_item]),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (tp.List[dt.datetime], ...),
            },
            model_kwargs={
                field: [fourth_date, fifth_date],
            },
        )

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__in_not_in__dates__list_as_string__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    now = dt.datetime.now()

    first_date = now + dt.timedelta(days=1)
    first_item = models_factory.ItemFactory.create(
        created_at=first_date,
    )

    second_date = now + dt.timedelta(days=2)
    second_item = models_factory.ItemFactory.create(
        created_at=second_date,
    )

    third_date = now + dt.timedelta(days=3)
    third_item = models_factory.ItemFactory.create(
        created_at=third_date,
    )

    fourth_date = now + dt.timedelta(days=4)
    fourth_item = models_factory.ItemFactory.create(
        created_at=fourth_date,
    )

    fifth_date = now + dt.timedelta(days=5)
    fifth_item = models_factory.ItemFactory.create(
        created_at=fifth_date,
    )

    assert db_session.query(models.Item).count() == 5

    for field, expected_items in (
        ("created_at__in", [fourth_item, fifth_item]),
        ("created_at__not_in", [first_item, second_item, third_item]),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (tp.List[dt.datetime], ...),
            },
            model_kwargs={
                field: f"{fourth_date}, {fifth_date}",
            },
        )

        filters_model.ConverterConfig.extra = {
            BaseModelConverterExtraParams.LIST_AS_STRING: {
                "fields": [
                    field,
                ],
                "expected_types": {
                    field: datetime.datetime,
                },
            }
        }

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__gt_lt_gte_lte__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    for i in range(1, 6):
        models_factory.ItemFactory.create(
            number=i,
        )

    assert db_session.query(models.Item).count() == 5

    for field, expected_item_numbers in (
        ("number__gt", [4, 5]),
        ("number__lt", [1, 2]),
        ("number__gte", [3, 4, 5]),
        ("number__lte", [1, 2, 3]),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (int, ...),
            },
            model_kwargs={
                field: 3,
            },
        )

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_item_numbers)

        for expected_item_number, result in zip(expected_item_numbers, results):
            assert result.number == expected_item_number


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__not__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    expected_item_names = [
        "expected_item_name_1",
        "expected_item_name_2",
        "expected_item_name_3",
    ]

    not_expected_item_name = "not_expected_item_name"

    expected_items = []
    for item_name in [*expected_item_names, not_expected_item_name]:
        expected_items.append(
            models_factory.ItemFactory.create(
                name=item_name,
            )
        )

    filters_model = get_sqlalchemy_filter_base_model(
        base_model=models.Item,
        field_kwargs={
            "name__not": (str, ...),
        },
        model_kwargs={
            "name__not": not_expected_item_name,
        },
    )

    assert db_session.query(models.Item).count() == 4

    if apply_filters:
        query = select(models.Item)
        query = filters_model.apply_filters(query=query)
        results = db_session.execute(query).scalars().all()
    else:
        results = (
            db_session.query(models.Item)
            .filter(*filters_model.to_binary_expressions())
            .all()
        )

    assert len(results) == len(expected_item_names)

    for expected_item, result in zip(expected_items, results):
        assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__is_is_not__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    valid_item = models_factory.ItemFactory.create(
        is_valid=True,
    )
    not_valid_item = models_factory.ItemFactory.create(is_valid=False)

    assert db_session.query(models.Item).count() == 2

    for is_valid, expected_items in (
        (
            False,
            [
                not_valid_item,
            ],
        ),
        (
            True,
            [
                valid_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                "is_valid__is": (bool, ...),
            },
            model_kwargs={
                "is_valid__is": is_valid,
            },
        )

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()

    for is_valid, expected_items in (
        (
            False,
            [
                valid_item,
            ],
        ),
        (
            True,
            [
                not_valid_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                "is_valid__is_not": (bool, ...),
            },
            model_kwargs={
                "is_valid__is_not": is_valid,
            },
        )

        results = (
            db_session.query(models.Item)
            .filter(*filters_model.to_binary_expressions())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__like_ilike__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    first_item = models_factory.ItemFactory.create(
        name="first name",
    )
    second_item = models_factory.ItemFactory.create(name="some oThEr NaMe")

    assert db_session.query(models.Item).count() == 2

    for field, filter_value, expected_items in (
        (
            "name__like",
            "%name%",
            [
                first_item,
            ],
        ),
        (
            "name__ilike",
            "%other name%",
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filter_base_model(
            base_model=models.Item,
            field_kwargs={
                field: (str, ...),
            },
            model_kwargs={
                field: filter_value,
            },
        )

        if apply_filters:
            query = select(models.Item)
            query = filters_model.apply_filters(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .filter(*filters_model.to_binary_expressions())
                .all()
            )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_filters",
    [
        True,
        False,
    ],
)
def test_filter__eq__dict_kwargs__ok(
    db_session,
    get_sqlalchemy_filter_base_model,
    apply_filters,
):
    expected_item_name = "expected_item_name"

    # Create expected item
    expected_item = models_factory.ItemFactory.create(name=expected_item_name)

    # Create unexpected items
    unexpected_items = models_factory.ItemFactory.create_batch(size=4)

    unexpected_items_ids = [unexpected_item.id for unexpected_item in unexpected_items]

    filters_model = get_sqlalchemy_filter_base_model(
        base_model=models.Item,
        field_kwargs={"name": (str, ...), "id__in": (tp.List[int], ...)},
        model_kwargs={
            "name": expected_item_name,
            "id__in": unexpected_items_ids,
        },
    )

    assert db_session.query(models.Item).count() == 5

    if apply_filters:
        query = select(models.Item)
        query = filters_model.apply_filters(
            query=query,
            export_params={
                "exclude": {"id__in"},
            },
        )
        results = db_session.execute(query).scalars().all()
    else:
        results = (
            db_session.query(models.Item)
            .filter(
                *filters_model.to_binary_expressions(
                    export_params={
                        "exclude": {"id__in"},
                    }
                )
            )
            .all()
        )

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()
