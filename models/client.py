from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.sql import func
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
    creation_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_update: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),
                                                  onupdate=datetime.now)
    sales_contact_id: Mapped[int | None] = mapped_column(ForeignKey('collaborator.id',
                                                                    ondelete='RESTRICT'),
                                                         nullable=False)
    collaborator: Mapped["Collaborator"] = relationship("Collaborator",
                                                        back_populates='clients')

    contracts: Mapped[list["Contract"]] = relationship("Contract",
                                                       back_populates='client')


    def __init__(self, full_name, email, phone_number, company, sales_contact_id):
        super().__init__()
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.company = company
        self.sales_contact_id = sales_contact_id

    def __repr__(self):
        return f"Client {self.full_name} : mail {self.email}, phone {self.phone_number}"

    def __str__(self):
        return f"Client {self.full_name} : mail {self.email}, phone {self.phone_number}"
