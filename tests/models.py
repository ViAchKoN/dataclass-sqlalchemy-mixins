import datetime as dt
import typing as tp

import sqlalchemy as sa
from sqlalchemy import Sequence
from sqlalchemy.orm import as_declarative, relationship


metadata = sa.MetaData()


@as_declarative(metadata=metadata)
class BaseModel:
    __abstract__ = True

    created_at = sa.Column(
        sa.DateTime(),
        nullable=False,
        default=dt.datetime.now,
    )

    def as_dict(self) -> tp.Dict[str, str]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore


class Owner(BaseModel):
    __tablename__ = "Owner"

    id_seq = Sequence("seq_parent_item_id", metadata=BaseModel.metadata)
    id = sa.Column(
        sa.Integer,
        primary_key=True,
        server_default=id_seq.next_value(),
    )
    first_name = sa.Column(
        sa.String,
        nullable=False,
    )
    last_name = sa.Column(
        sa.String,
        nullable=False,
    )
    email = sa.Column(sa.String, nullable=True)


class Group(BaseModel):
    __tablename__ = "group"

    id_seq = Sequence("seq_parent_item_id", metadata=BaseModel.metadata)
    id = sa.Column(
        sa.Integer,
        primary_key=True,
        server_default=id_seq.next_value(),
    )
    name = sa.Column(
        sa.String,
    )
    is_active = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
    )
    owner_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            Owner.id,
        ),
    )
    owner = relationship(Owner)

    items = relationship("Item", back_populates="group", lazy="dynamic")


class Item(BaseModel):
    __tablename__ = "item"

    id_seq = Sequence("seq_child_item_id", metadata=BaseModel.metadata)
    id = sa.Column(
        sa.Integer,
        primary_key=True,
        server_default=id_seq.next_value(),
    )
    name = sa.Column(
        sa.String,
    )
    number = sa.Column(
        sa.Integer,
    )
    is_valid = sa.Column(
        sa.Boolean,
        default=False,
        nullable=False,
    )

    group_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            Group.id,
        ),
    )

    group = relationship(Group)
