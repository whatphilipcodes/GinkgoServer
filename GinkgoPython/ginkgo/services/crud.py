from datetime import datetime, timedelta, timezone
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)
CreateT = TypeVar("CreateT")
ReadT = TypeVar("ReadT")


class BaseCRUD(Generic[T, CreateT, ReadT]):
    def __init__(
        self,
        model: Type[T],
        create_schema: Type[CreateT],
        read_schema: Type[ReadT],
        session: Session,
    ):
        self.model = model
        self.create_schema = create_schema
        self.read_schema = read_schema
        self.session = session

    def add(self, obj: CreateT) -> ReadT:
        db_obj = self.model.model_validate(obj)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return self.read_schema.model_validate(db_obj)  # type: ignore

    def get_by_id(self, record_id: int) -> Optional[ReadT]:
        stmt = select(self.model).where(self.model.id == record_id)  # type: ignore
        record = self.session.scalars(stmt).first()
        return self.read_schema.model_validate(record) if record else None  # type: ignore

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> list[ReadT]:
        stmt = select(self.model)
        if limit:
            order_field = getattr(self.model, "created_at", None) or getattr(
                self.model, "id", None
            )
            if order_field is not None:
                stmt = stmt.order_by(order_field.desc())
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        records = self.session.scalars(stmt).all()
        return [self.read_schema.model_validate(r) for r in records]  # type: ignore

    def get_recent(self, hours: int = 24) -> list[ReadT]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = select(self.model).where(self.model.created_at >= cutoff_time)  # type: ignore
        records = self.session.scalars(stmt).all()
        return [self.read_schema.model_validate(r) for r in records]  # type: ignore

    def get_by_field(self, field_name: str, field_value) -> list[ReadT]:
        field = getattr(self.model, field_name, None)
        if field is None:
            return []
        stmt = select(self.model).where(field == field_value)
        records = self.session.scalars(stmt).all()
        return [self.read_schema.model_validate(r) for r in records]  # type: ignore

    def update(self, record_id: int, update_data: dict) -> Optional[ReadT]:
        record = self.session.get(self.model, record_id)
        if record:
            for key, value in update_data.items():
                if value is not None and hasattr(record, key):
                    setattr(record, key, value)
            self.session.commit()
            self.session.refresh(record)
            return self.read_schema.model_validate(record)  # type: ignore
        return None

    def delete(self, record_id: int) -> bool:
        record = self.session.get(self.model, record_id)
        if record:
            self.session.delete(record)
            self.session.commit()
            return True
        return False

    def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        return int(self.session.exec(stmt).one())
