import datetime

from sqlalchemy import ForeignKey, String, Date, Time
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped
from sqlalchemy.sql.operators import truediv

from models import Base


class Event(Base):
    __tablename__ = 'event'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,
                                    nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    attendees: Mapped[int] = mapped_column(nullable=False)
    contract_id: Mapped[int] = mapped_column(ForeignKey('contract.id',
                                                        ondelete='CASCADE'),
                                             nullable=False)
    contract: Mapped["Contract"] = relationship('Contract', backref=backref(
        'events', uselist=False))
    sales_contact_id: Mapped[int] = mapped_column(ForeignKey('collaborator.id',
                                                             ondelete='SET NULL'),
                                                  nullable=True)
    collaborator: Mapped["Collaborator"] = relationship("Collaborator",
                                                        back_populates='events')

    def __repr__(self):
        return (f"Event {self.id} for contract {self.contract_id} start "
                f"{self.start_date} at {self.start_time} and end {self.end_date} at "
                f"{self.end_time}.\n It takes place on {self.location} and "
                f"{self.attendees} persons are expected.")
