import enum

from django.contrib.auth.models import Permission
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models import Base

class RoleType(enum.Enum):
    MANAGEMENT = "management"
    SALES = "sales"
    SUPPORT = "support"

class Role(Base):
    __tablename__ = 'collaborator_role'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Enum(RoleType), unique=True, nullable=False)


class Collaborator(Base):
    __tablename__ = 'collaborator'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(150), nullable=False)
    name = Column(String(150), nullable=False)
    phone_number = Column(String(15), nullable=False)
    role_id = Column(Integer, ForeignKey('collaborator_role.id'), nullable=False)
    role = relationship('Role', backref='collaborators')

    # def __init__(self, name, role):
    #     super().__init__()
    #     self.name = name
    #     self.first_name =
    #     self.role = role

    def __repr__(self):
        return f"Collaborator {self.name} : {self.role.name}"


    def has_permission(self, action, resource):
        return Permission.has_permission(self.role, action, resource)
