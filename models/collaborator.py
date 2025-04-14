from sqlalchemy import String, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models import Base
from utils import util
from utils.permissions import PermissionManager, RoleType


class Collaborator(Base):
    __tablename__ = "collaborator"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    role: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False)
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract", back_populates="collaborator"
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="collaborator")
    clients: Mapped[list["Client"]] = relationship(
        "Client", back_populates="collaborator"
    )

    def __init__(self, email, password, first_name, name, phone_number, role):
        super().__init__()
        self.email = email
        self.password = util.hash_password(password)
        self.phone_number = phone_number
        self.first_name = first_name
        self.name = name
        self.role = role

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            f"Collaborator {self.first_name} {self.name} : {self.role.value}. "
            f"Email: {self.email}, phone number: {self.phone_number}."
        )

    def has_permission(self, action, resource):
        return PermissionManager.has_permission(self.role.name, action, resource)
