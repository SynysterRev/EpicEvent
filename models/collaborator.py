from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models import Base

class Role(Base):
    __tablename__ = 'collaborator_role'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)

class Collaborator(Base):
    __tablename__ = 'collaborator'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(150), nullable=False)
    role_id = Column(Integer, ForeignKey('collaborator_role.id'), nullable=False)
    role = relationship('Role', backref='collaborators')

    def __repr__(self):
        return f"Collaborator {self.name} : {self.role.name}"

