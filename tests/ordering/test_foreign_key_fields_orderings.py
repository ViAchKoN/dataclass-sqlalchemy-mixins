import pytest
from sqlalchemy import select

from tests import models, models_factory


@pytest.mark.parametrize(
    ("query_type", "joined"),
    [
        ("select", True),
        ("select", False),
        ("query", True),
        ("query", False),
        (None, None),
    ],
)
def test_order_by_id__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    query_type,
    joined,
):
    items = []
    for i in range(5):
        items.append(
            models_factory.ItemFactory.create(
                group=models_factory.GroupFactory.create()
            )
        )

    for order_by in [
        "group__id",
        [
            "group__id",
        ],
        "-group__id",
        [
            "-group__id",
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
            "-group__id",
            [
                "-group__id",
            ],
        ]:
            expected_items = list(reversed(items))

        if query_type == "select":
            query = select(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        elif query_type == "query":
            query = db_session.query(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = query.all()
        else:
            query = db_session.query(models.Item).join(models.Group)

            query = query.order_by(*order_by_model.to_unary_expressions())

            results = query.all()

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    ("query_type", "joined"),
    [
        ("select", True),
        ("select", False),
        ("query", True),
        ("query", False),
        (None, None),
    ],
)
def test_order_by_dates__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    query_type,
    joined,
):
    items = []
    for i in range(5):
        items.append(
            models_factory.ItemFactory.create(
                group=models_factory.GroupFactory.create()
            )
        )

    for order_by in [
        "group__created_at",
        [
            "group__created_at",
        ],
        "-group__created_at",
        [
            "-group__created_at",
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
            "-group__created_at",
            [
                "-group__created_at",
            ],
        ]:
            expected_items = list(reversed(items))

        if query_type == "select":
            query = select(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        elif query_type == "query":
            query = db_session.query(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = query.all()
        else:
            query = db_session.query(models.Item).join(models.Group)

            query = query.order_by(*order_by_model.to_unary_expressions())

            results = query.all()

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


@pytest.mark.parametrize(
    ("query_type", "joined"),
    [
        ("select", True),
        ("select", False),
        ("query", True),
        ("query", False),
        (None, None),
    ],
)
def test_order_by_name__ok(
    db_session,
    get_sqlalchemy_order_base_model,
    query_type,
    joined,
):
    items = []
    for name in [
        "aar",
        "abc",
        "cat",
        "wow",
    ]:
        items.append(
            models_factory.ItemFactory.create(
                group=models_factory.GroupFactory.create(name=name)
            )
        )

    for order_by in [
        "group__name",
        [
            "group__name",
        ],
        "-group__name",
        [
            "-group__name",
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
            "-group__name",
            [
                "-group__name",
            ],
        ]:
            expected_items = list(reversed(items))

        if query_type == "select":
            query = select(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = db_session.execute(query).scalars().all()
        elif query_type == "query":
            query = db_session.query(models.Item)

            if joined:
                query = query.join(models.Group)

            query = order_by_model.apply_order_by(query=query)
            results = query.all()
        else:
            query = db_session.query(models.Item).join(models.Group)

            query = query.order_by(*order_by_model.to_unary_expressions())

            results = query.all()

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()
