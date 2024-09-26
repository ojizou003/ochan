import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID as PostgreUUID
from sqlalchemy.types import CHAR, TypeDecorator

from app import db
from config import (
    ANON_NAME_MAX_LENGTH,
    BOARD_CATEGORY_NAME_MAX_LENGTH,
    BOARD_NAME_MAX_LENGTH,
    BODY_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    THREAD_NAME_MAX_LENGTH,
)

class UUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class UUIDMixin:
    id = db.Column(UUID(), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Res(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "reses"
    number = db.Column(db.Integer, nullable=False)
    anon_name = db.Column(db.String(ANON_NAME_MAX_LENGTH), nullable=True)
    anon_email = db.Column(db.String(EMAIL_MAX_LENGTH), nullable=True)
    who = db.Column(db.String(22), nullable=False)
    body = db.Column(db.Text, nullable=False)
    thread_id = db.Column(UUID(), db.ForeignKey("threads.id"), nullable=False)


class Thread(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "threads"
    name = db.Column(db.String(THREAD_NAME_MAX_LENGTH), nullable=False)
    board_id = db.Column(UUID(), db.ForeignKey("boards.id"), nullable=False)
    reses = db.relationship("Res", backref="thread")

    @property
    def sorted_reses(self):
        return sorted(self.reses, key=lambda res: res.number)

    @property
    def reses_count(self) -> int:
        return len(self.reses)

    @property
    def next_res_number(self) -> int:
        return self.reses_count + 1

    @property
    def last_posted_at(self) -> datetime:
        last_res = (
            Res.query.filter_by(thread_id=self.id)
            .order_by(Res.created_at.desc())
            .first()
        )
        return last_res.created_at

class Board(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "boards"
    name = db.Column(db.String(BOARD_NAME_MAX_LENGTH), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(
        UUID(), db.ForeignKey("board_categories.id"), nullable=False
    )
    threads = db.relationship("Thread", backref="board")


class BoardCategory(UUIDMixin, TimestampMixin, db.Model):
    __tablename__ = "board_categories"
    name = db.Column(
        db.String(BOARD_CATEGORY_NAME_MAX_LENGTH), unique=True, nullable=False
    )
    boards = db.relationship("Board", backref="board_category")
