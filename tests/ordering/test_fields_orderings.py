import datetime as dt
import typing as tp
from dataclasses import dataclass

import pytest
from sqlalchemy import select

from dataclass_sqlalchemy_mixins.base import utils
from dataclass_sqlalchemy_mixins.base.mixins import SqlAlchemyOrderConverterMixin
from tests import models, models_factory


def test_order_by_id__dataclass__ok(
    db_session,
):
    items = models_factory.ItemFactory.create_batch(size=5)

    @dataclass
    class CustomDataclass(SqlAlchemyOrderConverterMixin):
        order_by: tp.Optional[tp.Union[str, tp.List[str]]] = None

        class ConverterConfig:
            model = models.Item

    for order_by in [
        "id",
        [
            "id",
        ],
        "-id",
        [
            "-id",
        ],
    ]:
        custom_dataclass = CustomDataclass(order_by=order_by)

        expected_items = items
        if order_by in [
            "-id",
            [
                "-id",
            ],
        ]:
            expected_items = list(reversed(items))

        results = (
            db_session.query(models.Item)
            .order_by(
                *custom_dataclass.get_unary_expressions(custom_dataclass.order_by)
            )
            .all()
        )

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_order_by_id__utils__ok(
    db_session,
):
    items = models_factory.ItemFactory.create_batch(size=5)

    for order_by in [
        "id",
        [
            "id",
        ],
        "-id",
        [
            "-id",
        ],
    ]:
        expected_items = items
        if order_by in [
            "-id",
            [
                "-id",
            ],
        ]:
            expected_items = list(reversed(items))

        results = (
            db_session.query(models.Item)
            .order_by(
                *utils.get_unary_expressions(
                    order_by=order_by,
                    model=models.Item,
                )
            )
            .all()
        )

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_order_by_id__utils__apply__ok(
    db_session,
):
    items = models_factory.ItemFactory.create_batch(size=5)

    for order_by in [
        "id",
        [
            "id",
        ],
        "-id",
        [
            "-id",
        ],
    ]:
        expected_items = items
        if order_by in [
            "-id",
            [
                "-id",
            ],
        ]:
            expected_items = list(reversed(items))

        query = db_session.query(models.Item)

        query = utils.apply_order_by(
            query=query,
            order_by=order_by,
            model=models.Item,
        )

        results = query.all()

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_order_by",
    [
        True,
        False,
    ],
)
def test_order_by_id__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    apply_order_by,
):
    items = models_factory.ItemFactory.create_batch(size=5)

    for order_by in [
        "id",
        [
            "id",
        ],
        "-id",
        [
            "-id",
        ],
    ]:
        order_by_model = get_sqlalchemy_order_base_model(
            base_model=models.Item,
            model_kwargs={
                "order_by": order_by,
            },
        )

        expected_items = items
        if order_by in [
            "-id",
            [
                "-id",
            ],
        ]:
            expected_items = list(reversed(items))

        if apply_order_by:
            query = select(models.Item)
            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .order_by(*order_by_model.to_unary_expressions())
                .all()
            )

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_order_by",
    [
        True,
        False,
    ],
)
def test_order_by_dates__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    apply_order_by,
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

    items = [first_item, second_item, third_item, fourth_item, fifth_item]

    for order_by in [
        "created_at",
        [
            "created_at",
        ],
        "-created_at",
        [
            "-created_at",
        ],
    ]:
        order_by_model = get_sqlalchemy_order_base_model(
            base_model=models.Item,
            model_kwargs={
                "order_by": order_by,
            },
        )

        expected_items = items
        if order_by in [
            "-created_at",
            [
                "-created_at",
            ],
        ]:
            expected_items = list(reversed(items))

        if apply_order_by:
            query = select(models.Item)
            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .order_by(*order_by_model.to_unary_expressions())
                .all()
            )

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    "apply_order_by",
    [
        True,
        False,
    ],
)
def test_order_by_name__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    apply_order_by,
):
    items = []

    for name in [
        "aar",
        "abc",
        "cat",
        "wow",
    ]:
        items.append(models_factory.ItemFactory.create(name=name))

    for order_by in [
        "name",
        [
            "name",
        ],
        "-name",
        [
            "-name",
        ],
    ]:
        order_by_model = get_sqlalchemy_order_base_model(
            base_model=models.Item,
            model_kwargs={
                "order_by": order_by,
            },
        )

        expected_items = items
        if order_by in [
            "-name",
            [
                "-name",
            ],
        ]:
            expected_items = list(reversed(items))

        if apply_order_by:
            query = select(models.Item)
            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        else:
            results = (
                db_session.query(models.Item)
                .order_by(*order_by_model.to_unary_expressions())
                .all()
            )

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()
