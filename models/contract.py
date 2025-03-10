import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models import Base


class Status(enum.Enum):
    signed = 1
    pending = 2
    canceled = 3


class Contract(Base):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    total_amount = Column(Integer, nullable=False)
    remaining_amount = Column(Integer, nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    status = Column(Enum(Status), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id',
                                           ondelete='SET NULL'), nullable=True)
    client = relationship('Client', backref='contracts')
    sales_contact_id = Column(Integer,
                              ForeignKey('collaborator.id', ondelete='SET NULL'),
                              nullable=True)
    collaborator = relationship('Collaborator', backref='contracts')

    def __repr__(self):
        return (f"Contract {self.id} for client {self.client.full_name} is "
                f"{self.status}.\n "
                f"Total amount {self.total_amount}, remaining amount {self.remaining_amount}.")
