"""
SQLAlchemy database models and session management.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rig_query.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WorkPack(Base):
    __tablename__ = "work_packs"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String)  # Active, In Progress, Completed, Pending
    priority = Column(String)  # High, Medium, Low
    created_date = Column(String)
    description = Column(Text, nullable=True)
    procedures = relationship("Procedure", back_populates="work_pack")
    checklists = relationship("Checklist", back_populates="work_pack")


class Procedure(Base):
    __tablename__ = "procedures"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String)  # Pending, In Progress, Completed
    assigned_to = Column(String, nullable=True)
    work_pack_id = Column(Integer, ForeignKey("work_packs.id"))
    work_pack = relationship("WorkPack", back_populates="procedures")
    operations = relationship("Operation", back_populates="procedure")


class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    step_order = Column(Integer)
    status = Column(String)  # Pending, In Progress, Completed
    procedure_id = Column(Integer, ForeignKey("procedures.id"))
    procedure = relationship("Procedure", back_populates="operations")


class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    operator_name = Column(String)
    shift_type = Column(String)  # Morning, Afternoon, Night
    login_time = Column(String)
    logout_time = Column(String, nullable=True)
    status = Column(String)  # Active, Completed
    date = Column(String)


class Checklist(Base):
    __tablename__ = "checklists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    equipment = Column(String)
    created_date = Column(String)
    work_pack_id = Column(Integer, ForeignKey("work_packs.id"), nullable=True)
    work_pack = relationship("WorkPack", back_populates="checklists")
    items = relationship("ChecklistItem", back_populates="checklist")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    is_required = Column(Boolean, default=True)
    step_number = Column(Integer)
    checklist_id = Column(Integer, ForeignKey("checklists.id"))
    checklist = relationship("Checklist", back_populates="items")


class EquipmentKB(Base):
    __tablename__ = "equipment_kb"
    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String)
    content = Column(Text)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
