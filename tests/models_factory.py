import datetime as dt

import factory

from tests import conftest, models


class CustomSQLAlchemyModelFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with conftest.db_test_session() as session:
            session.expire_on_commit = False
            obj = model_class(*args, **kwargs)
            session.add(obj)
            session.commit()
            session.expunge_all()
        return obj


class OwnerFactory(CustomSQLAlchemyModelFactory):
    class Meta:
        model = models.Owner

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    created_at = factory.LazyFunction(lambda: dt.datetime.now())


class GroupFactory(CustomSQLAlchemyModelFactory):
    class Meta:
        model = models.Group

    created_at = factory.LazyFunction(lambda: dt.datetime.now())
    name = factory.Faker("word")
    is_active = factory.Faker("boolean")
    owner = factory.SubFactory(OwnerFactory)

    class Params:
        with_item = factory.Trait(
            _factory_boy_group=factory.RelatedFactory(
                "tests.models_factory.ItemFactory",
                factory_related_name="group",
            ),
        )


class ItemFactory(CustomSQLAlchemyModelFactory):
    class Meta:
        model = models.Item

    created_at = factory.LazyFunction(lambda: dt.datetime.now())
    name = factory.Faker("word")
    number = factory.Faker("pyint")
    is_valid = factory.Faker("boolean")
    group = None
