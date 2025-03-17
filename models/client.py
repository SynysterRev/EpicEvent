from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models import Base


class Client(Base):
    __tablename__ = 'client'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    company: Mapped[str] = mapped_column(String(150), nullable=False,
                                         default='Not specified')
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.now,
                                                  onupdate=datetime.now)
    sales_contact_id: Mapped[int | None] = mapped_column(ForeignKey('collaborator.id',
                                                                    ondelete='RESTRICT'),
                                                         nullable=False)
    collaborator: Mapped["Collaborator"] = relationship("Collaborator",
                                                        back_populates='clients')

    contracts: Mapped[list["Contract"]] = relationship("Contract",
                                                       back_populates='client')

    def __repr__(self):
        return f"Client {self.full_name} : mail {self.email}, phone {self.phone_number}"
