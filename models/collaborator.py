import enum

from sqlalchemy import Column, Integer, String, Enum
from models import Base

class Role(enum.Enum):
    sales = 1
    support = 2
    management = 3

class Collaborator(Base):
    __tablename__ = 'collaborator'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(Enum(Role), nullable=False)

    def __repr__(self):
        return f"Collaborator {self.name} : {self.role}"

