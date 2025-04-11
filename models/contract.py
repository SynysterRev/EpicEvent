import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models import Base


class Status(enum.Enum):
    SIGNED = "signed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(nullable=False)
    remaining_amount: Mapped[float] = mapped_column(nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    client_id: Mapped[int] = mapped_column(
        ForeignKey(
            "client.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")

    sales_contact_id: Mapped[int] = mapped_column(
        ForeignKey("collaborator.id", ondelete="SET NULL"), nullable=True
    )
    collaborator: Mapped["Collaborator"] = relationship(
        "Collaborator", back_populates="contracts"
    )

    def __init__(
        self, total_amount, remaining_amount, status, client_id, sales_contact_id=None
    ):
        super().__init__()
        self.total_amount = total_amount.replace(',', '.')
        self.remaining_amount = remaining_amount.replace(',', '.')
        self.status = status
        self.client_id = client_id
        self.sales_contact_id = sales_contact_id

    def __repr__(self):
        return (
            f"Contract {self.id} for client: {self.client.full_name} is "
            f"{self.status.value}.\n "
            f"Total amount: {self.total_amount}€, remaining amount:"
            f" {self.remaining_amount}€."
            f" Sales contact: {self.collaborator.first_name}"
            f" {self.collaborator.name}."
        )
