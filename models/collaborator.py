from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models import Base
from utils import util
from utils.permissions import PermissionManager, RoleType


class Role(Base):
    __tablename__ = 'collaborator_role'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    nullable=False)
    name: Mapped[RoleType] = mapped_column(Enum(RoleType), unique=True, nullable=False)
    collaborators: Mapped[list["Collaborator"]] = relationship("Collaborator",
                                                               back_populates='role')


class Collaborator(Base):
    __tablename__ = 'collaborator'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey('collaborator_role.id'),
                                         nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates='collaborators')
    contracts: Mapped[list["Contract"]] = relationship("Contract",
                                                       back_populates='collaborator')
    events: Mapped[list["Event"]] = relationship("Event", back_populates='collaborator')
    clients: Mapped[list["Client"]] = relationship("Client",
                                                   back_populates='collaborator')

    def __init__(self, email, password, first_name, name, phone_number, role_id):
        super().__init__()
        self.email = email
        self.password = util.hash_password(password)
        self.phone_number = phone_number
        self.first_name = first_name
        self.name = name
        self.role_id = role_id


    def __repr__(self):
        return f"Collaborator {self.first_name} {self.name} : {self.role.name}"

    def __str__(self):
        return (f"Collaborator {self.first_name} {self.name} : {self.role.name}. "
                f"Email: {self.email}, phone number: {self.phone_number}.")

    def has_permission(self, action, resource):
        return PermissionManager.has_permission(self.role.name, action, resource)
