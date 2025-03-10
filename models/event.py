from sqlalchemy import Column, Integer, ForeignKey, String, DATE, TIME
from sqlalchemy.orm import relationship, backref

from models import Base


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    start_date = Column(DATE, nullable=False)
    start_time = Column(TIME, nullable=False)
    end_date = Column(DATE, nullable=False)
    end_time = Column(TIME, nullable=False)
    location = Column(String(200), nullable=False)
    attendees = Column(Integer, nullable=False)
    contract_id = Column(Integer, ForeignKey('contract.id',
                                             ondelete='CASCADE'), nullable=True)
    contract = relationship('Contract', backref=backref('events', uselist=False))
    sales_contact_id = Column(Integer,
                              ForeignKey('collaborator.id', ondelete='SET NULL'),
                              nullable=True)
    collaborator = relationship('Collaborator', backref='contracts')

    def __repr__(self):
        return (f"Event {self.id} for contract {self.contract_id} start "
                f"{self.start_date} at {self.start_time} and end {self.end_date} at "
                f"{self.end_time}.\n It takes place on {self.location} and "
                f"{self.attendees} persons are expected.")
