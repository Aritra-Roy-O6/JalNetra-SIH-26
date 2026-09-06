"""SQLAlchemy models and PostgreSQL initialization for JalNetra."""

import os

from dotenv import load_dotenv
from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/orca_db",
)
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Alert(Base):
    """A hazard or regulatory alert associated with a geographic zone."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    zone_geom = Column(JSON, nullable=False)


class Advisory(Base):
    """Marine advisory text and its semantic-search embedding."""

    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    embedding = Column(Vector(1536))


def initialize_database() -> None:
    """Enable pgvector and create tables if they do not already exist."""
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(connection)


if __name__ == "__main__":
    initialize_database()
    print("Database tables initialized successfully.")