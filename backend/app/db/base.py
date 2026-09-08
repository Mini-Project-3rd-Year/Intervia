"""Declarative base for application-owned database tables."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass