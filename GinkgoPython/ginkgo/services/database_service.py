from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, create_engine, select

from ginkgo.core.config import settings
from ginkgo.models import (
    Decree,
    DecreeRead,
    GSODAttribute,
    GSODTrait,
    Prompt,
    PromptRead,
    Thought,
    ThoughtRead,
)
from ginkgo.schemas.frontend import InputLanguage, InputSource


class DatabaseService:
    """Service for managing input records (thoughts, prompts, decrees)"""

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

    # —— Thought operations ——————————————————————————————————
    def add_thought(
        self,
        text: str,
        lang: InputLanguage,
        source: InputSource = InputSource.AUDIENCE,
        valid: bool = True,
        attribute_class: Optional[GSODAttribute] = None,
        trait: Optional[GSODTrait] = None,
    ) -> ThoughtRead:
        """Add a new thought record.

        Returns:
            ThoughtRead: The persisted record with id and timestamps
        """
        with self.get_session() as session:
            record = Thought(
                text=text,
                lang=lang,
                source=source,
                valid=valid,
                attribute_class=attribute_class,
                trait=trait,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return ThoughtRead.model_validate(record)

    def get_thought_by_id(self, record_id: int) -> Optional[ThoughtRead]:
        """Get a thought record by ID.

        Returns:
            ThoughtRead if found, None otherwise
        """
        with self.get_session() as session:
            stmt = select(Thought).where(Thought.id == record_id)
            record = session.scalars(stmt).first()
            return ThoughtRead.model_validate(record) if record else None

    def get_thoughts_by_source(
        self,
        source: InputSource,
    ) -> list[ThoughtRead]:
        """Get all thoughts filtered by source.

        Returns:
            List of ThoughtRead
        """
        with self.get_session() as session:
            stmt = select(Thought).where(Thought.source == source)
            records = session.scalars(stmt).all()
            return [ThoughtRead.model_validate(r) for r in records]

    def get_all_thoughts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[ThoughtRead]:
        """Get all thoughts with pagination.

        Returns:
            List of ThoughtRead
        """
        with self.get_session() as session:
            stmt = select(Thought)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            records = session.scalars(stmt).all()
            return [ThoughtRead.model_validate(r) for r in records]

    def get_recent_thoughts(
        self,
        hours: int = 24,
    ) -> list[ThoughtRead]:
        """Get recent thoughts within the specified hours.

        Returns:
            List of ThoughtRead
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = select(Thought).where(Thought.created_at >= cutoff_time)
            records = session.scalars(stmt).all()
            return [ThoughtRead.model_validate(r) for r in records]

    def update_thought(
        self,
        record_id: int,
        new_text: str,
        valid: Optional[bool] = None,
        attribute_class: Optional[GSODAttribute] = None,
        trait: Optional[GSODTrait] = None,
        trait_offset: Optional[float] = None,
        trait_entailment: Optional[float] = None,
        score_health: Optional[float] = None,
        score_split: Optional[float] = None,
        score_impact: Optional[float] = None,
    ) -> Optional[ThoughtRead]:
        """Update a thought record.

        Returns:
            ThoughtRead if found and updated, None otherwise
        """
        with self.get_session() as session:
            record = session.get(Thought, record_id)
            if record:
                record.text = new_text
                if valid is not None:
                    record.valid = valid
                if attribute_class is not None:
                    record.attribute_class = attribute_class
                if trait is not None:
                    record.trait = trait
                if trait_offset is not None:
                    record.trait_offset = trait_offset
                if trait_entailment is not None:
                    record.trait_entailment = trait_entailment
                if score_health is not None:
                    record.score_health = score_health
                if score_split is not None:
                    record.score_split = score_split
                if score_impact is not None:
                    record.score_impact = score_impact
                session.commit()
                session.refresh(record)
                return ThoughtRead.model_validate(record)
            return None

    def delete_thought(self, record_id: int) -> bool:
        """Delete a thought record"""
        with self.get_session() as session:
            record = session.get(Thought, record_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def count_thoughts(self) -> int:
        """Count all thoughts"""
        with self.get_session() as session:
            stmt = select(func.count()).select_from(Thought)
            return int(session.exec(stmt).one())

    # —— Prompt operations ———————————————————————————————————
    def add_prompt(
        self,
        text: str,
        lang: InputLanguage,
        source: InputSource = InputSource.AUDIENCE,
        valid: bool = True,
    ) -> PromptRead:
        """Add a new prompt record.

        Returns:
            PromptRead: The persisted record with id and timestamps
        """
        with self.get_session() as session:
            record = Prompt(
                text=text,
                lang=lang,
                source=source,
                valid=valid,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return PromptRead.model_validate(record)

    def get_prompt_by_id(self, record_id: int) -> Optional[PromptRead]:
        """Get a prompt record by ID.

        Returns:
            PromptRead if found, None otherwise
        """
        with self.get_session() as session:
            stmt = select(Prompt).where(Prompt.id == record_id)
            record = session.scalars(stmt).first()
            return PromptRead.model_validate(record) if record else None

    def get_prompts_by_source(
        self,
        source: InputSource,
    ) -> list[PromptRead]:
        """Get all prompts filtered by source.

        Returns:
            List of PromptRead
        """
        with self.get_session() as session:
            stmt = select(Prompt).where(Prompt.source == source)
            records = session.scalars(stmt).all()
            return [PromptRead.model_validate(r) for r in records]

    def get_all_prompts(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[PromptRead]:
        """Get all prompts with pagination.

        Returns:
            List of PromptRead
        """
        with self.get_session() as session:
            stmt = select(Prompt)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            records = session.scalars(stmt).all()
            return [PromptRead.model_validate(r) for r in records]

    def get_recent_prompts(
        self,
        hours: int = 24,
    ) -> list[PromptRead]:
        """Get recent prompts within the specified hours.

        Returns:
            List of PromptRead
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = select(Prompt).where(Prompt.created_at >= cutoff_time)
            records = session.scalars(stmt).all()
            return [PromptRead.model_validate(r) for r in records]

    def update_prompt(
        self,
        record_id: int,
        new_text: str,
        valid: Optional[bool] = None,
    ) -> Optional[PromptRead]:
        """Update the text of a prompt record.

        Returns:
            PromptRead if found and updated, None otherwise
        """
        with self.get_session() as session:
            record = session.get(Prompt, record_id)
            if record:
                record.text = new_text
                if valid is not None:
                    record.valid = valid
                session.commit()
                session.refresh(record)
                return PromptRead.model_validate(record)
            return None

    def delete_prompt(self, record_id: int) -> bool:
        """Delete a prompt record"""
        with self.get_session() as session:
            record = session.get(Prompt, record_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def count_prompts(self) -> int:
        """Count all prompts"""
        with self.get_session() as session:
            stmt = select(func.count()).select_from(Prompt)
            return int(session.exec(stmt).one())

    # —— Decree operations ———————————————————————————————————
    def add_decree(
        self,
        text: str,
        lang: InputLanguage,
        source: InputSource = InputSource.AUDIENCE,
        valid: bool = True,
    ) -> DecreeRead:
        """Add a new decree record.

        Returns:
            DecreeRead: The persisted record with id and timestamps
        """
        with self.get_session() as session:
            record = Decree(
                text=text,
                lang=lang,
                source=source,
                valid=valid,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return DecreeRead.model_validate(record)

    def get_decree_by_id(self, record_id: int) -> Optional[DecreeRead]:
        """Get a decree record by ID.

        Returns:
            DecreeRead if found, None otherwise
        """
        with self.get_session() as session:
            stmt = select(Decree).where(Decree.id == record_id)
            record = session.scalars(stmt).first()
            return DecreeRead.model_validate(record) if record else None

    def get_decrees_by_source(
        self,
        source: InputSource,
    ) -> list[DecreeRead]:
        """Get all decrees filtered by source.

        Returns:
            List of DecreeRead
        """
        with self.get_session() as session:
            stmt = select(Decree).where(Decree.source == source)
            records = session.scalars(stmt).all()
            return [DecreeRead.model_validate(r) for r in records]

    def get_all_decrees(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
    ) -> list[DecreeRead]:
        """Get all decrees with pagination.

        Returns:
            List of DecreeRead
        """
        with self.get_session() as session:
            stmt = select(Decree)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            records = session.scalars(stmt).all()
            return [DecreeRead.model_validate(r) for r in records]

    def get_recent_decrees(
        self,
        hours: int = 24,
    ) -> list[DecreeRead]:
        """Get recent decrees within the specified hours.

        Returns:
            List of DecreeRead
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        with self.get_session() as session:
            stmt = select(Decree).where(Decree.created_at >= cutoff_time)
            records = session.scalars(stmt).all()
            return [DecreeRead.model_validate(r) for r in records]

    def update_decree(
        self,
        record_id: int,
        new_text: str,
        valid: Optional[bool] = None,
    ) -> Optional[DecreeRead]:
        """Update the text of a decree record.

        Returns:
            DecreeRead if found and updated, None otherwise
        """
        with self.get_session() as session:
            record = session.get(Decree, record_id)
            if record:
                record.text = new_text
                if valid is not None:
                    record.valid = valid
                session.commit()
                session.refresh(record)
                return DecreeRead.model_validate(record)
            return None

    def delete_decree(self, record_id: int) -> bool:
        """Delete a decree record"""
        with self.get_session() as session:
            record = session.get(Decree, record_id)
            if record:
                session.delete(record)
                session.commit()
                return True
            return False

    def count_decrees(self) -> int:
        """Count all decrees"""
        with self.get_session() as session:
            stmt = select(func.count()).select_from(Decree)
            return int(session.exec(stmt).one())


db_service = DatabaseService()
