import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models import Base


class Status(enum.Enum):
    signed = 1
    pending = 2
    canceled = 3


class Contract(Base):
    __tablename__ = 'contract'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    nullable=False)
    total_amount: Mapped[int] = mapped_column(nullable=False)
    remaining_amount: Mapped[int] = mapped_column(nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey('client.id',
                                                      ondelete='RESTRICT', ),
                                           nullable=False)
    client: Mapped["Client"] = relationship("Client", back_populates='contracts')

    sales_contact_id: Mapped[int] = mapped_column(
        ForeignKey('collaborator.id', ondelete='RESTRICT'),
        nullable=False)
    collaborator: Mapped["Collaborator"] = relationship("Collaborator",
                                                        back_populates='contracts')

    def __repr__(self):
        return (f"Contract {self.id} for client {self.client.full_name} is "
                f"{self.status}.\n "
                f"Total amount {self.total_amount}, remaining amount {self.remaining_amount}.")
