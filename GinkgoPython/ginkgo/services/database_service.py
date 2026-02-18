from datetime import datetime
from typing import Optional

from sqlmodel import Session, create_engine, select

from ginkgo.core.config import settings
from ginkgo.models import UserInputRecord
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
    ) -> UserInputRecord:
        """Add a new user input record"""
        with self.get_session() as session:
            record = UserInputRecord(
                text=text,
                type=input_type,
                lang=lang,
                source=source,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_by_id(self, record_id: int) -> Optional[UserInputRecord]:
        """Get a user input record by ID"""
        with self.get_session() as session:
            stmt = select(UserInputRecord).where(UserInputRecord.id == record_id)
            return session.scalars(stmt).first()

    def get_by_type(
        self,
        input_type: InputType,
        limit: Optional[int] = None,
    ) -> list[UserInputRecord]:
        """Get all user inputs filtered by type"""
        with self.get_session() as session:
            stmt = (
                select(UserInputRecord)
                .where(UserInputRecord.type == input_type)
                .order_by(UserInputRecord.created_at.desc())
            )
            if limit:
                stmt = stmt.limit(limit)
            return list(session.scalars(stmt).all())

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[UserInputRecord]:
        """Get all user inputs with pagination"""
        with self.get_session() as session:
            stmt = (
                select(UserInputRecord)
                .order_by(UserInputRecord.created_at.desc())
                .offset(offset)
            )
            if limit:
                stmt = stmt.limit(limit)
            return list(session.scalars(stmt).all())

    def get_recent(
        self,
        hours: int = 24,
        input_type: Optional[InputType] = None,
    ) -> list[UserInputRecord]:
        """Get recent user inputs within the specified hours"""
        from datetime import timedelta, timezone

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = (
                select(UserInputRecord)
                .where(UserInputRecord.created_at >= cutoff_time)
                .order_by(UserInputRecord.created_at.desc())
            )
            if input_type:
                stmt = stmt.where(UserInputRecord.type == input_type)
            return list(session.scalars(stmt).all())

    def update_text(self, record_id: int, new_text: str) -> Optional[UserInputRecord]:
        """Update the text of a user input record"""
        with self.get_session() as session:
            record = session.get(UserInputRecord, record_id)
            if record:
                record.text = new_text
                session.commit()
                session.refresh(record)
            return record

    def delete(self, record_id: int) -> bool:
        """Delete a user input record"""
        with self.get_session() as session:
            record = session.get(UserInputRecord, record_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def count_by_type(self, input_type: InputType) -> int:
        """Count records by type"""
        with self.get_session() as session:
            stmt = select(UserInputRecord).where(UserInputRecord.type == input_type)
            return len(list(session.scalars(stmt).all()))


db_service = DatabaseService()
