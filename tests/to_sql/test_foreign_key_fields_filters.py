import datetime as dt

from tests import models, models_factory


def test_filter__eq__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    # Create expected group and item
    expected_group_name = "expected_group_name"

    expected_group = models_factory.GroupFactory.create(
        name=expected_group_name, with_item=True
    )
    expected_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == expected_group.id)
        .first()
    )

    # Create unexpected groups and items
    models_factory.GroupFactory.create_batch(with_item=True, size=4)

    assert db_session.query(models.Item).count() == 5

    filters_model = get_sqlalchemy_filters_model(
        base_model=models.Item,
        field_kwargs={
            "group__name": (str, ...),
        },
        model_kwargs={
            "group__name": expected_group_name,
        },
    )

    results = (
        db_session.query(models.Item)
        .join(models.Group)
        .filter(*filters_model.to_sql())
        .all()
    )

    assert len(results) == 1

    result = results[0]

    assert result.as_dict() == expected_item.as_dict()


def test_filter__in_not_in__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    first_group_name = "first_group_name"

    first_group = models_factory.GroupFactory.create(
        name=first_group_name, with_item=True
    )
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == first_group.id)
        .first()
    )

    second_group_name = "second_group_name"

    second_group = models_factory.GroupFactory.create(
        name=second_group_name, with_item=True
    )
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == second_group.id)
        .first()
    )

    for field, filter_values, expected_items in (
        (
            "group__name__in",
            [first_group_name, second_group_name],
            [first_item, second_item],
        ),
        ("group__name__not_in", [first_group_name, second_group_name], []),
        (
            "group__name__in",
            [
                first_group_name,
            ],
            [
                first_item,
            ],
        ),
        (
            "group__name__not_in",
            [
                first_group_name,
            ],
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (list[str], ...),
            },
            model_kwargs={
                field: filter_values,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_filter__in_not_in__dates__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    now = dt.datetime.now()

    first_date = now + dt.timedelta(days=1)

    first_group = models_factory.GroupFactory.create(
        created_at=first_date, with_item=True
    )
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == first_group.id)
        .first()
    )

    second_date = now + dt.timedelta(days=2)

    second_group = models_factory.GroupFactory.create(
        created_at=second_date, with_item=True
    )
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == second_group.id)
        .first()
    )

    for field, filter_values, expected_items in (
        ("group__created_at__in", [first_date, second_date], [first_item, second_item]),
        ("group__created_at__not_in", [first_date, second_date], []),
        (
            "group__created_at__in",
            [
                first_date,
            ],
            [
                first_item,
            ],
        ),
        (
            "group__created_at__not_in",
            [
                first_date,
            ],
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (list[dt.datetime], ...),
            },
            model_kwargs={
                field: filter_values,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_filter__gt_lt_gte_lte__date__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    now = dt.datetime.now()

    first_date = now + dt.timedelta(days=1)

    first_group = models_factory.GroupFactory.create(
        created_at=first_date, with_item=True
    )
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == first_group.id)
        .first()
    )

    second_date = now + dt.timedelta(days=2)

    second_group = models_factory.GroupFactory.create(
        created_at=second_date, with_item=True
    )
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == second_group.id)
        .first()
    )

    third_date = now + dt.timedelta(days=3)

    for field, filter_values, expected_items in (
        ("group__created_at__gt", now, [first_item, second_item]),
        ("group__created_at__lt", third_date, [first_item, second_item]),
        (
            "group__created_at__gte",
            second_date,
            [
                second_item,
            ],
        ),
        (
            "group__created_at__lte",
            first_date,
            [
                first_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (dt.datetime, ...),
            },
            model_kwargs={
                field: filter_values,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_filter__not__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    first_group_name = "first_group_name"

    first_group = models_factory.GroupFactory.create(
        name=first_group_name, with_item=True
    )
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == first_group.id)
        .first()
    )

    second_group_name = "second_group_name"

    second_group = models_factory.GroupFactory.create(
        name=second_group_name, with_item=True
    )
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == second_group.id)
        .first()
    )

    fake_name = "fake_name"

    for field, filter_values, expected_items in (
        ("group__name__not", fake_name, [first_item, second_item]),
        (
            "group__name__not",
            second_group_name,
            [
                first_item,
            ],
        ),
        (
            "group__name__not",
            first_group_name,
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (str, ...),
            },
            model_kwargs={
                field: filter_values,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_filter__is_is_not__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    active_group = models_factory.GroupFactory.create(is_active=True, with_item=True)
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == active_group.id)
        .first()
    )

    inactive_group = models_factory.GroupFactory.create(is_active=False, with_item=True)
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == inactive_group.id)
        .first()
    )

    for field, filter_values, expected_items in (
        ("group__is_active__is", True, [first_item]),
        (
            "group__is_active__is",
            False,
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (bool, ...),
            },
            model_kwargs={
                field: filter_values,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()


def test_filter__like_ilike__ok(
    db_session,
    get_sqlalchemy_filters_model,
):
    first_group = models_factory.GroupFactory.create(name="first name", with_item=True)
    first_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == first_group.id)
        .first()
    )

    second_group = models_factory.GroupFactory.create(
        name="some oThEr NaMe", with_item=True
    )
    second_item = (
        db_session.query(models.Item)
        .filter(models.Item.group_id == second_group.id)
        .first()
    )

    assert db_session.query(models.Item).count() == 2

    for field, filter_value, expected_items in (
        (
            "group__name__like",
            "%name%",
            [
                first_item,
            ],
        ),
        (
            "group__name__ilike",
            "%other name%",
            [
                second_item,
            ],
        ),
    ):
        filters_model = get_sqlalchemy_filters_model(
            base_model=models.Item,
            field_kwargs={
                field: (str, ...),
            },
            model_kwargs={
                field: filter_value,
            },
        )

        results = (
            db_session.query(models.Item)
            .join(models.Group)
            .filter(*filters_model.to_sql())
            .all()
        )

        assert len(results) == len(expected_items)

        for expected_item, result in zip(expected_items, results):
            assert result.as_dict() == expected_item.as_dict()
