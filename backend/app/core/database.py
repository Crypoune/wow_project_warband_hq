from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy."""

    pass


engine = create_engine(settings.database_url)

# Fabrique les sessions SQLAlchemy utilisées pour accéder à PostgreSQL.
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
