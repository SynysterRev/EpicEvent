import datetime

from sqlalchemy import ForeignKey, String, Date, Time, Text
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped

from models import Base


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    attendees: Mapped[int] = mapped_column(nullable=False)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contract.id", ondelete="CASCADE"), nullable=False
    )
    contract: Mapped["Contract"] = relationship(
        "Contract", backref=backref("events", uselist=False)
    )
    support_contact_id: Mapped[int] = mapped_column(
        ForeignKey("collaborator.id", ondelete="SET NULL"), nullable=True
    )
    collaborator: Mapped["Collaborator"] = relationship(
        "Collaborator", back_populates="events"
    )
    note: Mapped[str] = mapped_column(Text, nullable=True)

    def __init__(
            self,
            start_date,
            start_time,
            end_date,
            end_time,
            location,
            attendees,
            contract_id,
            support_contact_id,
            note="",
    ):
        super().__init__()
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.location = location
        self.attendees = attendees
        self.contract_id = contract_id
        self.support_contact_id = support_contact_id
        self.note = note

    def __str__(self):
        support_contact_info = (
            f"Support contact: {self.collaborator.first_name} {self.collaborator.name}."
            if self.collaborator is not None
            else "Support contact: No support assigned."
        )

        event_info = (
            f"Event {self.id} for contract {self.contract_id} start "
            f"{self.start_date} at {self.start_time} and end {self.end_date} at "
            f"{self.end_time}.\nIt takes place on {self.location} and "
            f"{self.attendees} persons are expected.\n"
            f"Support contact: {support_contact_info}\n"
            f"Note: {self.note}"
        )
        return event_info

    def __repr__(self):
        return str(self)
