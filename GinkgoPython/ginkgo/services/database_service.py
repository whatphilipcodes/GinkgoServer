from datetime import datetime
from typing import Optional

from sqlalchemy import desc, func
from sqlmodel import Session, create_engine, select

from ginkgo.core.config import settings
from ginkgo.models import InputRecord
from ginkgo.schemas.frontend import InputLanguage, InputSource, InputType


class DatabaseService:
    """Service for managing user input records"""

    def __init__(self):
        """Initialize database connection and create tables"""
        self.engine = create_engine(
            f"sqlite:///{settings.database_path}",
            echo=settings.database_echo,
        )

        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return Session(self.engine)

    def add_input(
        self,
        text: str,
        input_type: InputType,
        lang: InputLanguage,
        source: InputSource = InputSource.AUDIENCE,
    ) -> InputRecord:
        """Add a new user input record"""
        with self.get_session() as session:
            record = InputRecord(
                text=text,
                type=input_type,
                lang=lang,
                source=source,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_by_id(self, record_id: int) -> Optional[InputRecord]:
        """Get a user input record by ID"""
        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.id == record_id)
            return session.scalars(stmt).first()

    def get_by_source(
        self,
        source: InputSource,
    ) -> list[InputRecord]:
        """Get all user inputs filtered by source"""
        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.source == source)
            return list(session.scalars(stmt).all())

    def get_by_type(
        self,
        input_type: InputType,
        limit: Optional[int] = None,
    ) -> list[InputRecord]:
        """Get all user inputs filtered by type"""
        with self.get_session() as session:
            stmt = (
                select(InputRecord)
                .where(InputRecord.type == input_type)
                .order_by(desc(InputRecord.created_at))
            )
            if limit:
                stmt = stmt.limit(limit)
            return list(session.scalars(stmt).all())

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[InputRecord]:
        """Get all user inputs with pagination"""
        with self.get_session() as session:
            stmt = (
                select(InputRecord)
                .order_by(desc(InputRecord.created_at))
                .offset(offset)
            )
            if limit:
                stmt = stmt.limit(limit)
            return list(session.scalars(stmt).all())

    def get_recent(
        self,
        hours: int = 24,
        input_type: Optional[InputType] = None,
    ) -> list[InputRecord]:
        """Get recent user inputs within the specified hours"""
        from datetime import timedelta, timezone

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = (
                select(InputRecord)
                .where(InputRecord.created_at >= cutoff_time)
                .order_by(desc(InputRecord.created_at))
            )
            if input_type:
                stmt = stmt.where(InputRecord.type == input_type)
            return list(session.scalars(stmt).all())

    def update_text(self, record_id: int, new_text: str) -> Optional[InputRecord]:
        """Update the text of a user input record"""
        with self.get_session() as session:
            record = session.get(InputRecord, record_id)
            if record:
                record.text = new_text
                session.commit()
                session.refresh(record)
            return record

    def delete(self, record_id: int) -> bool:
        """Delete a user input record"""
        with self.get_session() as session:
            record = session.get(InputRecord, record_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def count_by_type(self, input_type: InputType) -> int:
        """Count records by type"""
        with self.get_session() as session:
            stmt = select(func.count()).select_from(InputRecord).where(
                InputRecord.type == input_type
            )
            return int(session.exec(stmt).one())


db_service = DatabaseService()
