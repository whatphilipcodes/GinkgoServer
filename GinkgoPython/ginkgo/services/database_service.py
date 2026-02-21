from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, create_engine, select

from ginkgo.core.config import settings
from ginkgo.models import InputRecord, InputRecordCreate, InputRecordRead
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
    ) -> InputRecordRead:
        """Add a new user input record.

        Returns:
            InputRecordRead: The persisted record with id and timestamps
        """
        with self.get_session() as session:
            # Validate input using InputRecordCreate, but create InputRecord for persistence
            validated = InputRecordCreate(
                text=text,
                type=input_type,
                lang=lang,
                source=source,
            )
            record = InputRecord(
                text=validated.text,
                type=validated.type,
                lang=validated.lang,
                source=validated.source,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return InputRecordRead.model_validate(record)

    def get_by_id(self, record_id: int) -> Optional[InputRecordRead]:
        """Get a user input record by ID.

        Returns:
            InputRecordRead if found, None otherwise
        """
        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.id == record_id)
            record = session.scalars(stmt).first()
            return InputRecordRead.model_validate(record) if record else None

    def get_by_source(
        self,
        source: InputSource,
    ) -> list[InputRecordRead]:
        """Get all user inputs filtered by source.

        Returns:
            List of InputRecordRead (always have valid id from database)
        """
        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.source == source)
            records = session.scalars(stmt).all()
            return [InputRecordRead.model_validate(r) for r in records]

    def get_by_type(
        self,
        input_type: InputType,
        limit: Optional[int] = None,
    ) -> list[InputRecordRead]:
        """Get all user inputs filtered by type.

        Returns:
            List of InputRecordRead (always have valid id from database)
        """
        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.type == input_type)
            # Order by created_at descending
            stmt = stmt.order_by(getattr(InputRecord, "created_at").desc())
            if limit:
                stmt = stmt.limit(limit)
            records = session.scalars(stmt).all()
            return [InputRecordRead.model_validate(r) for r in records]

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[InputRecordRead]:
        """Get all user inputs with pagination.

        Returns:
            List of InputRecordRead (always have valid id from database)
        """
        with self.get_session() as session:
            stmt = select(InputRecord).order_by(
                getattr(InputRecord, "created_at").desc()
            )
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            records = session.scalars(stmt).all()
            return [InputRecordRead.model_validate(r) for r in records]

    def get_recent(
        self,
        hours: int = 24,
        input_type: Optional[InputType] = None,
    ) -> list[InputRecordRead]:
        """Get recent user inputs within the specified hours.

        Returns:
            List of InputRecordRead (always have valid id from database)
        """
        from datetime import timedelta, timezone

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = select(InputRecord).where(InputRecord.created_at >= cutoff_time)
            if input_type:
                stmt = stmt.where(InputRecord.type == input_type)
            stmt = stmt.order_by(getattr(InputRecord, "created_at").desc())
            records = session.scalars(stmt).all()
            return [InputRecordRead.model_validate(r) for r in records]

    def update_text(self, record_id: int, new_text: str) -> Optional[InputRecordRead]:
        """Update the text of a user input record.

        Returns:
            InputRecordRead if found and updated, None otherwise
        """
        with self.get_session() as session:
            record = session.get(InputRecord, record_id)
            if record:
                record.text = new_text
                session.commit()
                session.refresh(record)
                return InputRecordRead.model_validate(record)
            return None

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
            stmt = (
                select(func.count())
                .select_from(InputRecord)
                .where(InputRecord.type == input_type)
            )
            return int(session.exec(stmt).one())


db_service = DatabaseService()
